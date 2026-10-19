using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Http.Json;
using Microsoft.AspNetCore.Server.Kestrel.Core;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

namespace UniversalCouncil.CommandCenter.RemoteTransport;

public sealed record RemoteTransportHostOptions(
    string RemoteOwnerProjectionPath,
    string RemoteTransportProjectionPath,
    string RegistryPath,
    string RuntimeRoot,
    int Port);

public static class RemoteTransportHost
{
    public static WebApplication Build(
        RemoteTransportHostOptions options,
        Func<DateTimeOffset>? utcNow = null)
    {
        if (options.Port is < 0 or > 65535)
        {
            throw new InvalidOperationException("Remote transport port is outside the valid range.");
        }

        utcNow ??= () => DateTimeOffset.UtcNow;

        var transportReader = new JsonRemoteTransportReader(
            Path.GetFullPath(options.RemoteTransportProjectionPath));
        var transportProjection = new RemoteTransportProjectionService(
            transportReader).GetTransport();

        if (transportProjection.Health != RemoteTransportHealth.Healthy ||
            transportProjection.ListenerScope != "LOOPBACK_ONLY" ||
            transportProjection.PublicExposureAllowed ||
            transportProjection.LiveExecutionAuthorized)
        {
            throw new InvalidOperationException(
                $"Remote transport policy is unavailable or unsafe: {transportProjection.ProblemLabel}");
        }

        var ownerReader = new JsonRemoteOwnerGatewayReader(
            Path.GetFullPath(options.RemoteOwnerProjectionPath));
        var registry = new JsonDeviceSessionRegistry(
            Path.GetFullPath(options.RegistryPath));

        Directory.CreateDirectory(Path.GetFullPath(options.RuntimeRoot));
        var trust = new RemoteCommandTrustService(
            ownerReader,
            registry,
            new FileRemoteReplayLedger(
                Path.Combine(options.RuntimeRoot, "remote-command-replay.jsonl")),
            new AppendOnlyRemoteCommandQueue(
                Path.Combine(options.RuntimeRoot, "remote-command-queue.jsonl")),
            utcNow);

        var builder = WebApplication.CreateSlimBuilder();
        builder.Logging.ClearProviders();
        builder.Services.Configure<JsonOptions>(json =>
        {
            json.SerializerOptions.PropertyNamingPolicy =
                JsonNamingPolicy.SnakeCaseLower;
            json.SerializerOptions.PropertyNameCaseInsensitive = false;
            json.SerializerOptions.UnmappedMemberHandling =
                JsonUnmappedMemberHandling.Disallow;
        });

        builder.WebHost.ConfigureKestrel(server =>
        {
            server.AddServerHeader = false;
            server.Limits.MaxRequestBodySize =
                transportProjection.MaxRequestBodyBytes;
            server.Listen(
                IPAddress.Loopback,
                options.Port,
                listen => listen.Protocols = HttpProtocols.Http1);
        });

        var app = builder.Build();

        app.MapGet("/healthz", () =>
            Results.Json(new
            {
                status = "ok",
                scope = "loopback-only"
            }));

        app.MapGet("/v1/status", (HttpRequest request) =>
        {
            var authorization = Authenticate(
                request,
                registry,
                utcNow());

            return Results.Json(new
            {
                authenticated = authorization.Authenticated,
                transport = transportProjection.Mode,
                listener_scope = transportProjection.ListenerScope,
                target_host = transportProjection.TargetHost,
                tailscale_connected = transportProjection.TailscaleConnected,
                phone_connected = transportProjection.PhoneConnected,
                execution_state = transportProjection.ExecutionState,
                live_execution_authorized =
                    transportProjection.LiveExecutionAuthorized
            });
        });

        app.MapPost("/v1/commands", async (HttpRequest request) =>
        {
            EnforceJsonRequest(request, transportProjection.MaxRequestBodyBytes);
            var authorization = Authenticate(
                request,
                registry,
                utcNow());

            var envelope = await request.ReadFromJsonAsync<RemoteCommandEnvelope>()
                ?? throw new BadHttpRequestException(
                    "Remote command body is required.",
                    StatusCodes.Status400BadRequest);

            var receipt = trust.EnqueueAuthenticatedTransport(
                envelope,
                authorization);

            return Results.Json(receipt);
        });

        app.MapPost("/v1/approvals/validate", async (HttpRequest request) =>
        {
            EnforceJsonRequest(request, transportProjection.MaxRequestBodyBytes);
            var authorization = Authenticate(
                request,
                registry,
                utcNow());

            var approval = await request.ReadFromJsonAsync<RemoteApprovalRequest>()
                ?? throw new BadHttpRequestException(
                    "Approval body is required.",
                    StatusCodes.Status400BadRequest);

            var validated = trust.BuildAndValidateApproval(
                approval,
                authorization);

            return Results.Json(new
            {
                approval_id = validated.ApprovalId,
                state = "VALID_NOT_EXECUTION_AUTHORITY"
            });
        });

        app.UseExceptionHandler(errorApp =>
        {
            errorApp.Run(async context =>
            {
                var feature = context.Features.Get<
                    Microsoft.AspNetCore.Diagnostics.IExceptionHandlerFeature>();
                var exception = feature?.Error;

                context.Response.ContentType = "application/json";
                context.Response.StatusCode = exception switch
                {
                    BadHttpRequestException bad => bad.StatusCode,
                    RemoteOwnerGatewayException =>
                        StatusCodes.Status401Unauthorized,
                    JsonException =>
                        StatusCodes.Status400BadRequest,
                    _ => StatusCodes.Status500InternalServerError
                };

                await context.Response.WriteAsJsonAsync(new
                {
                    error = context.Response.StatusCode switch
                    {
                        StatusCodes.Status401Unauthorized =>
                            "authentication_or_policy_rejected",
                        StatusCodes.Status400BadRequest =>
                            "invalid_request",
                        StatusCodes.Status413PayloadTooLarge =>
                            "payload_too_large",
                        StatusCodes.Status415UnsupportedMediaType =>
                            "json_required",
                        _ => "transport_failure"
                    }
                });
            });
        });

        return app;
    }

    private static OwnerAuthorizationContext Authenticate(
        HttpRequest request,
        IRemoteTransportAuthenticator authenticator,
        DateTimeOffset now)
    {
        if (!AuthenticationHeaderValue.TryParse(
                request.Headers.Authorization,
                out var header) ||
            !string.Equals(
                header.Scheme,
                "Bearer",
                StringComparison.OrdinalIgnoreCase) ||
            string.IsNullOrWhiteSpace(header.Parameter))
        {
            throw new RemoteOwnerGatewayException(
                "Bearer authentication is required.");
        }

        var deviceId = request.Headers["X-UC-Device-ID"].ToString();
        var sessionId = request.Headers["X-UC-Session-ID"].ToString();

        return authenticator.Authenticate(
            header.Parameter,
            deviceId,
            sessionId,
            now);
    }

    private static void EnforceJsonRequest(
        HttpRequest request,
        int maxRequestBodyBytes)
    {
        if (request.ContentLength is > 0 &&
            request.ContentLength > maxRequestBodyBytes)
        {
            throw new BadHttpRequestException(
                "Request body exceeds Stage 6 maximum.",
                StatusCodes.Status413PayloadTooLarge);
        }

        if (string.IsNullOrWhiteSpace(request.ContentType) ||
            !request.ContentType.StartsWith(
                "application/json",
                StringComparison.OrdinalIgnoreCase))
        {
            throw new BadHttpRequestException(
                "Stage 6 POST endpoints require application/json.",
                StatusCodes.Status415UnsupportedMediaType);
        }
    }
}

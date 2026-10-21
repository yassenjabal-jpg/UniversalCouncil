using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonGatewayRoutingPolicyReader : IGatewayRoutingPolicyReader
{
    private readonly string path;

    public JsonGatewayRoutingPolicyReader(string path)
    {
        this.path = path;
    }

    public GatewayRoutingPolicyDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new GatewayRoutingPolicyException(
                $"Gateway routing policy is missing: {path}");
        }

        try
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
            };

            return JsonSerializer.Deserialize<GatewayRoutingPolicyDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new GatewayRoutingPolicyException(
                    "Gateway routing policy is empty.");
        }
        catch (GatewayRoutingPolicyException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new GatewayRoutingPolicyException(
                $"Cannot read Gateway routing policy: {exc.Message}",
                exc);
        }
    }
}

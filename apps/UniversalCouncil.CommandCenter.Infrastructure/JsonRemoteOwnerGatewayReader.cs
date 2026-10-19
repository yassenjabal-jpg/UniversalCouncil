using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonRemoteOwnerGatewayReader : IRemoteOwnerGatewayReader
{
    private readonly string path;

    public JsonRemoteOwnerGatewayReader(string path)
    {
        this.path = path;
    }

    public RemoteOwnerGatewayDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new RemoteOwnerGatewayException(
                $"Remote Owner gateway projection is missing: {path}");
        }

        try
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
            };

            return JsonSerializer.Deserialize<RemoteOwnerGatewayDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new RemoteOwnerGatewayException(
                    "Remote Owner gateway projection is empty.");
        }
        catch (RemoteOwnerGatewayException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new RemoteOwnerGatewayException(
                $"Cannot read Remote Owner gateway projection: {exc.Message}",
                exc);
        }
    }
}

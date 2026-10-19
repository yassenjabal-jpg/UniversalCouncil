using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonRemoteTransportReader : IRemoteTransportReader
{
    private readonly string path;

    public JsonRemoteTransportReader(string path)
    {
        this.path = path;
    }

    public RemoteTransportDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new RemoteOwnerGatewayException(
                $"Remote transport projection is missing: {path}");
        }

        try
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
            };

            return JsonSerializer.Deserialize<RemoteTransportDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new RemoteOwnerGatewayException(
                    "Remote transport projection is empty.");
        }
        catch (RemoteOwnerGatewayException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new RemoteOwnerGatewayException(
                $"Cannot read Remote Transport projection: {exc.Message}",
                exc);
        }
    }
}

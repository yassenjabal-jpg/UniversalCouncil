using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonOwnerTailnetReader : IOwnerTailnetReader
{
    private readonly string path;

    public JsonOwnerTailnetReader(string path)
    {
        this.path = Path.GetFullPath(path);
    }

    public OwnerTailnetDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new RemoteOwnerGatewayException(
                $"Stage 7 owner-tailnet projection is missing: {path}");
        }

        try
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
            };

            return JsonSerializer.Deserialize<OwnerTailnetDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new RemoteOwnerGatewayException(
                    "Stage 7 owner-tailnet projection is empty.");
        }
        catch (RemoteOwnerGatewayException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new RemoteOwnerGatewayException(
                $"Cannot read Stage 7 owner-tailnet projection: {exc.Message}",
                exc);
        }
    }
}

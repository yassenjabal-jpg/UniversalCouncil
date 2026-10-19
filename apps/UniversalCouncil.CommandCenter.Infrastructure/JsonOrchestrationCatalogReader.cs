using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonOrchestrationCatalogReader : IOrchestrationCatalogReader
{
    private readonly string path;

    public JsonOrchestrationCatalogReader(string path)
    {
        this.path = path;
    }

    public OrchestrationCatalogDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new OrchestrationCatalogReadException(
                $"Orchestration catalog is missing: {path}");
        }

        try
        {
            var json = File.ReadAllText(path);
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
            };

            return JsonSerializer.Deserialize<OrchestrationCatalogDocument>(json, options)
                ?? throw new OrchestrationCatalogReadException(
                    "Orchestration catalog is empty.");
        }
        catch (OrchestrationCatalogReadException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new OrchestrationCatalogReadException(
                $"Cannot read orchestration catalog: {exc.Message}",
                exc);
        }
    }
}

using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonProjectContextMapReader : IProjectContextMapReader
{
    private readonly string path;

    public JsonProjectContextMapReader(string path)
    {
        this.path = path;
    }

    public ProjectContextMapDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new ProjectContextReadException(
                $"Project context map is missing: {path}");
        }

        try
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
            };

            return JsonSerializer.Deserialize<ProjectContextMapDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new ProjectContextReadException(
                    "Project context map is empty.");
        }
        catch (ProjectContextReadException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new ProjectContextReadException(
                $"Cannot read project context map: {exc.Message}",
                exc);
        }
    }
}

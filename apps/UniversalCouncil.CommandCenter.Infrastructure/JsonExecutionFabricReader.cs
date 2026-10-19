using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonExecutionFabricReader : IExecutionFabricReader
{
    private readonly string path;

    public JsonExecutionFabricReader(string path)
    {
        this.path = path;
    }

    public ExecutionFabricDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new ExecutionFabricReadException(
                $"Execution fabric is missing: {path}");
        }

        try
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
            };

            return JsonSerializer.Deserialize<ExecutionFabricDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new ExecutionFabricReadException(
                    "Execution fabric is empty.");
        }
        catch (ExecutionFabricReadException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new ExecutionFabricReadException(
                $"Cannot read execution fabric: {exc.Message}",
                exc);
        }
    }
}

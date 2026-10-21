using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonCapabilityRegistryReader : ICapabilityRegistryReader
{
    private readonly string path;

    public JsonCapabilityRegistryReader(string path)
    {
        this.path = path;
    }

    public CapabilityRegistryDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new CapabilityRegistryException(
                $"Capability Registry is missing: {path}");
        }

        try
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
            };

            return JsonSerializer.Deserialize<CapabilityRegistryDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new CapabilityRegistryException(
                    "Capability Registry is empty.");
        }
        catch (CapabilityRegistryException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new CapabilityRegistryException(
                $"Cannot read Capability Registry: {exc.Message}",
                exc);
        }
    }
}

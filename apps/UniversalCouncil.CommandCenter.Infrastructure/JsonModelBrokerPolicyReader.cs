using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonModelBrokerPolicyReader : IModelBrokerPolicyReader
{
    private readonly string path;

    public JsonModelBrokerPolicyReader(string path)
    {
        this.path = path;
    }

    public ModelBrokerPolicyDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new ModelBrokerException(
                $"Model Broker policy is missing: {path}");
        }

        try
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
            };

            return JsonSerializer.Deserialize<ModelBrokerPolicyDocument>(
                File.ReadAllText(path),
                options)
                ?? throw new ModelBrokerException(
                    "Model Broker policy is empty.");
        }
        catch (ModelBrokerException)
        {
            throw;
        }
        catch (Exception exc) when (
            exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new ModelBrokerException(
                $"Cannot read Model Broker policy: {exc.Message}",
                exc);
        }
    }
}

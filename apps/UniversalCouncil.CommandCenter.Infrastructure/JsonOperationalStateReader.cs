using System.Text.Json;
using UniversalCouncil.CommandCenter.Application;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class JsonOperationalStateReader : IOperationalStateReader
{
    private readonly string path;

    public JsonOperationalStateReader(string path)
    {
        this.path = path;
    }

    public OperationalStateDocument Read()
    {
        if (!File.Exists(path))
        {
            throw new OperationalStateReadException(
                $"Operational state file is missing: {path}");
        }

        try
        {
            var json = File.ReadAllText(path);
            using var parsed = JsonDocument.Parse(json);

            var allowedRootProperties = new HashSet<string>(StringComparer.Ordinal)
            {
                "schema_version",
                "source_type",
                "source_label",
                "baseline_revision",
                "project_id",
                "project_label",
                "stage_id",
                "stage_label",
                "stage_state",
                "execution_enabled",
                "phase_gate_label",
                "evidence",
                "approvals",
                "usage",
                "execution_manifest"
            };

            foreach (var property in parsed.RootElement.EnumerateObject())
            {
                if (!allowedRootProperties.Contains(property.Name))
                {
                    throw new OperationalStateReadException(
                        $"Unsupported operational state field: {property.Name}");
                }
            }

            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = false,
                UnmappedMemberHandling = System.Text.Json.Serialization.JsonUnmappedMemberHandling.Disallow
            };

            var dto = JsonSerializer.Deserialize<JsonStateDto>(json, options)
                ?? throw new OperationalStateReadException("Operational state document is empty.");

            return dto.ToDocument();
        }
        catch (OperationalStateReadException)
        {
            throw;
        }
        catch (Exception exc) when (exc is IOException or JsonException or UnauthorizedAccessException)
        {
            throw new OperationalStateReadException(
                $"Cannot read operational state: {exc.Message}",
                exc);
        }
    }

    private sealed record JsonStateDto(
        [property: System.Text.Json.Serialization.JsonPropertyName("schema_version")] string SchemaVersion,
        [property: System.Text.Json.Serialization.JsonPropertyName("source_type")] string SourceType,
        [property: System.Text.Json.Serialization.JsonPropertyName("source_label")] string SourceLabel,
        [property: System.Text.Json.Serialization.JsonPropertyName("baseline_revision")] string BaselineRevision,
        [property: System.Text.Json.Serialization.JsonPropertyName("project_id")] string ProjectId,
        [property: System.Text.Json.Serialization.JsonPropertyName("project_label")] string ProjectLabel,
        [property: System.Text.Json.Serialization.JsonPropertyName("stage_id")] string StageId,
        [property: System.Text.Json.Serialization.JsonPropertyName("stage_label")] string StageLabel,
        [property: System.Text.Json.Serialization.JsonPropertyName("stage_state")] string StageState,
        [property: System.Text.Json.Serialization.JsonPropertyName("execution_enabled")] bool ExecutionEnabled,
        [property: System.Text.Json.Serialization.JsonPropertyName("phase_gate_label")] string PhaseGateLabel,
        [property: System.Text.Json.Serialization.JsonPropertyName("evidence")] IReadOnlyList<EvidenceDto> Evidence,
        [property: System.Text.Json.Serialization.JsonPropertyName("approvals")] IReadOnlyList<ApprovalDto> Approvals,
        [property: System.Text.Json.Serialization.JsonPropertyName("usage")] UsageDto Usage,
        [property: System.Text.Json.Serialization.JsonPropertyName("execution_manifest")] ExecutionManifestDto ExecutionManifest)
    {
        public OperationalStateDocument ToDocument() =>
            new(
                SchemaVersion,
                SourceType,
                SourceLabel,
                BaselineRevision,
                ProjectId,
                ProjectLabel,
                StageId,
                StageLabel,
                StageState,
                ExecutionEnabled,
                PhaseGateLabel,
                Evidence.Select(item => item.ToDocument()).ToArray(),
                Approvals.Select(item => item.ToDocument()).ToArray(),
                Usage.ToDocument(),
                ExecutionManifest.ToDocument());
    }

    private sealed record EvidenceDto(
        [property: System.Text.Json.Serialization.JsonPropertyName("id")] string Id,
        [property: System.Text.Json.Serialization.JsonPropertyName("category")] string Category,
        [property: System.Text.Json.Serialization.JsonPropertyName("title")] string Title,
        [property: System.Text.Json.Serialization.JsonPropertyName("result")] string Result,
        [property: System.Text.Json.Serialization.JsonPropertyName("reference")] string Reference,
        [property: System.Text.Json.Serialization.JsonPropertyName("digest")] string? Digest,
        [property: System.Text.Json.Serialization.JsonPropertyName("occurred_at")] string OccurredAt)
    {
        public EvidenceDocument ToDocument() =>
            new(Id, Category, Title, Result, Reference, Digest, OccurredAt);
    }

    private sealed record ApprovalDto(
        [property: System.Text.Json.Serialization.JsonPropertyName("id")] string Id,
        [property: System.Text.Json.Serialization.JsonPropertyName("title")] string Title,
        [property: System.Text.Json.Serialization.JsonPropertyName("state")] string State,
        [property: System.Text.Json.Serialization.JsonPropertyName("scope")] string Scope,
        [property: System.Text.Json.Serialization.JsonPropertyName("evidence_reference")] string EvidenceReference)
    {
        public ApprovalDocument ToDocument() =>
            new(Id, Title, State, Scope, EvidenceReference);
    }

    private sealed record UsageDto(
        [property: System.Text.Json.Serialization.JsonPropertyName("state")] string State,
        [property: System.Text.Json.Serialization.JsonPropertyName("provider")] string Provider,
        [property: System.Text.Json.Serialization.JsonPropertyName("recorded_model_calls")] long? RecordedModelCalls,
        [property: System.Text.Json.Serialization.JsonPropertyName("recorded_cost_usd")] decimal? RecordedCostUsd,
        [property: System.Text.Json.Serialization.JsonPropertyName("note")] string Note)
    {
        public UsageDocument ToDocument() =>
            new(State, Provider, RecordedModelCalls, RecordedCostUsd, Note);
    }

    private sealed record ExecutionManifestDto(
        [property: System.Text.Json.Serialization.JsonPropertyName("state")] string State,
        [property: System.Text.Json.Serialization.JsonPropertyName("gate")] string Gate,
        [property: System.Text.Json.Serialization.JsonPropertyName("last_manifest_id")] string? LastManifestId,
        [property: System.Text.Json.Serialization.JsonPropertyName("note")] string Note)
    {
        public ExecutionManifestDocument ToDocument() =>
            new(State, Gate, LastManifestId, Note);
    }
}

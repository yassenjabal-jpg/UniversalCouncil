using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

var source = Path.Combine(
    AppContext.BaseDirectory,
    "state",
    "project-context-map.json");

Require(File.Exists(source), "Project context map fixture is missing");

var reader = new JsonProjectContextMapReader(source);
var document = reader.Read();
var resolver = new ProjectContextResolver(reader);
var compiler = new ContextCapsuleCompiler();

var request = new ContextResolutionRequest(
    "universal-council-command-center",
    ["context", "ux"],
    ["agentic-os-policy", "context-capsule-contract", "ux-state-contract"],
    ["project", "context", "ux"],
    IncludeUntrustedData: false,
    MaxSources: 6);

var current = resolver.Resolve(request);
Require(current.State == ContextResolutionState.Current, "Canonical context must resolve CURRENT");
Require(current.Sources.Count >= 3, "Canonical context must contain the required sources");
Require(current.Sources.All(item => item.Freshness == "CURRENT"), "Current resolution contains stale sources");
Require(current.Conflicts.Count == 0, "Canonical context unexpectedly contains conflicts");

var compileRequest = new ContextCapsuleCompileRequest(
    "VALIDATION-CONTEXT-001",
    new DateTimeOffset(2026, 10, 21, 0, 0, 0, TimeSpan.Zero),
    ["al-murtakaz-mandatory-approval"],
    ["READ_CONTEXT", "PLAN_CONTEXT"],
    ["LIVE_EXECUTION", "STAGE8"],
    "context-resolver:1.0",
    "al-murtakaz-mandatory-approval:1.0",
    "MATERIAL_READ_ONLY",
    ["RESOLVED_CONTEXT", "COMPILED_CAPSULE"],
    ["CURRENT_CONTEXT", "DETERMINISTIC_CAPSULE_ID"]);

var first = compiler.Compile(current, compileRequest);
var second = compiler.Compile(current, compileRequest);

Require(first.State == ContextResolutionState.Current, "Current context must compile");
Require(first.Capsule is not null, "Current context must produce a capsule");
Require(second.Capsule is not null, "Repeated compilation must produce a capsule");
Require(
    first.Capsule.CapsuleId == second.Capsule.CapsuleId,
    "Identical context/request must produce a deterministic capsule id");
Require(
    first.Capsule.CapsuleId.StartsWith("CTX-", StringComparison.Ordinal),
    "Capsule id prefix drifted");
Require(
    first.Capsule.Sources.All(item =>
        item.AuthorityClass != "UNTRUSTED_EXTERNAL_DATA" || !item.CanGovern),
    "Untrusted data may not govern a capsule");

var staleDocument = document with
{
    Sources = document.Sources
        .Select(item =>
            item.Id == "context-capsule-contract"
                ? item with { Freshness = "STALE" }
                : item)
        .ToArray()
};

var stale = new ProjectContextResolver(
    new StaticProjectContextMapReader(staleDocument)).Resolve(request);

Require(
    stale.State == ContextResolutionState.StaleContext,
    "STALE selected source must return STALE_CONTEXT");

var staleCompilation = compiler.Compile(stale, compileRequest);
Require(
    staleCompilation.State == ContextResolutionState.StaleContext &&
    staleCompilation.Capsule is null,
    "STALE_CONTEXT must fail closed at capsule compilation");

var conflictDocument = document with
{
    Conflicts =
    [
        new(
            "validation-context-conflict",
            "Two governing context sources disagree.",
            ["agentic-os-policy", "context-capsule-contract"],
            ["context"],
            RequiresOwnerDecision: true,
            ChangeOfTruthRequired: true)
    ]
};

var conflict = new ProjectContextResolver(
    new StaticProjectContextMapReader(conflictDocument)).Resolve(request);

Require(
    conflict.State == ContextResolutionState.ContextConflict,
    "Governing source conflict must return CONTEXT_CONFLICT");
Require(conflict.Conflicts.Count == 1, "Conflict provenance must be preserved");
Require(conflict.ChangeOfTruthRequired, "Change-of-Truth conflict flag must be preserved");

var conflictCompilation = compiler.Compile(conflict, compileRequest);
Require(
    conflictCompilation.State == ContextResolutionState.ContextConflict &&
    conflictCompilation.Capsule is null,
    "CONTEXT_CONFLICT must fail closed at capsule compilation");

var untrustedSource = new ProjectContextSourceDocument(
    "validation-untrusted-source",
    "external://validation-note",
    new string('a', 40),
    "UNTRUSTED_EXTERNAL_DATA",
    "CURRENT",
    ["context"],
    ["project", "context"],
    Untrusted: true);

var untrustedDocument = document with
{
    Sources = document.Sources.Concat([untrustedSource]).ToArray()
};

var untrustedRequest = request with
{
    RequiredSourceIds =
    [
        "agentic-os-policy",
        "context-capsule-contract",
        "ux-state-contract",
        "validation-untrusted-source"
    ],
    IncludeUntrustedData = true,
    MaxSources = 7
};

var untrustedResolution = new ProjectContextResolver(
    new StaticProjectContextMapReader(untrustedDocument)).Resolve(untrustedRequest);

Require(
    untrustedResolution.State == ContextResolutionState.Current,
    "Explicitly included untrusted data should remain usable as non-governing context");

var untrustedCompilation = compiler.Compile(untrustedResolution, compileRequest);
Require(untrustedCompilation.Capsule is not null, "Untrusted-data context should still compile");
Require(
    untrustedCompilation.Capsule.Sources
        .Single(item => item.Id == "validation-untrusted-source")
        .CanGovern is false,
    "Untrusted content gained governing authority");

var changedResolution = current with
{
    Sources = current.Sources
        .Select(item =>
            item.Id == "context-capsule-contract"
                ? item with { BlobSha = new string('f', 40) }
                : item)
        .ToArray()
};

var changedCompilation = compiler.Compile(changedResolution, compileRequest);
Require(changedCompilation.Capsule is not null, "Changed current context should compile");
Require(
    first.Capsule.CapsuleId != changedCompilation.Capsule.CapsuleId,
    "Changing a source digest must change the capsule id");

Console.WriteLine("Command Center Context Resolver/Capsule Compiler validation: PASS");
return 0;

static void Require(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}

sealed class StaticProjectContextMapReader : IProjectContextMapReader
{
    private readonly ProjectContextMapDocument document;

    public StaticProjectContextMapReader(ProjectContextMapDocument document)
    {
        this.document = document;
    }

    public ProjectContextMapDocument Read() => document;
}

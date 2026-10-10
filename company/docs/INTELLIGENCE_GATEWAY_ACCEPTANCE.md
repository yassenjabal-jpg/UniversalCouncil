# Intelligence Gateway Acceptance — v1

Status: implementation acceptance criteria

The gateway is accepted only when all of the following remain true:

- Default authority is **READ_ONLY / PUBLIC_ONLY**.
- Native-first routing keeps GitHub and private/native sources on their stronger connectors.
- Agent Reach is restricted to the approved public-read operation allowlist.
- There is **no OpenCLI** path in v1.
- Authenticated Instagram, Facebook, Reddit, X/Twitter, LinkedIn and Xiaohongshu remain blocked.
- No install, configure, cookie extraction, credential ingestion, browser-extension enablement, publishing, messaging, purchasing or other external-write path exists in the v1 provider.
- Provider health cannot override policy.
- Strict Agent Reach pinning uses commit `94f06c1969dfc1834001269d79d3ad0972d9dee6`.
- Evidence provenance records provider, backend, source, auth, freshness, limitations and explicit fallback.
- Provider content cannot promote itself to a stronger evidence class or alter authority.
- A material blocked/unavailable source may create a capability-gap for HR review only.
- A capability-gap never grants install/auth/credential authority.
- The gateway remains routing infrastructure, not a Council member, and has no decision authority.
- Full company tests, config invariants, compile checks and security regression checks must pass before merge.

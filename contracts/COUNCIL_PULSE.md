# Council Pulse Contract — v0.3

Council Pulse is the Council's recurring self-review loop.

Its purpose is not to reopen everything repeatedly. Its purpose is to detect when an active decision has become weaker than the evidence now supports or when a material capability change can alter the feasible decision/execution set.

## Pulse checks
For every active project or material decision, check:
- external change;
- explicit decision-expiry trigger;
- unresolved pivotal unknowns;
- stale assumptions;
- execution-enthusiasm bias;
- sunk-cost attachment;
- cheaper/free substitutes;
- free-AI substitution;
- Foundation Model Uplift risk;
- user/operator burden;
- capability gaps affecting evidence, execution, speed, quality or risk;
- material tooling or external capability advances;
- whether bounded HR capability scouting is due;
- ignored blockers or dissent;
- stronger rejected alternatives;
- commitment-evidence quality;
- success-metric drift.

A capability change does not automatically justify adoption. It opens or updates only the affected capability-gap slice and routes serious candidates through the applicable security, architecture/duplication, sandbox and Owner gates.

## Pulse outputs
- NO-CHANGE
- WATCH
- REOPEN-SLICE
- REOPEN-DECISION
- PIVOT-RECOMMENDED
- KILL-RECOMMENDED
- USER-DECISION-REQUIRED

## Notification rule
Do not interrupt the user for NO-CHANGE. A capability scan with no material finding is NO-CHANGE. Surface only material findings, newly pivotal unknowns, or actions that require the user's authority.

## Anti-churn rule
A decision is not reopened merely because a different option or new tool exists. Reopen only when new evidence, a failed assumption, an expiry trigger, a meaningful execution signal, a superior alternative, or a material capability change can plausibly change the decision.

## Scope rule
Pulse evaluates active decisions under the same evidence hierarchy and domain authority as normal Council work. Community evidence may reveal edge cases and lived experience but does not automatically override stronger authoritative evidence.

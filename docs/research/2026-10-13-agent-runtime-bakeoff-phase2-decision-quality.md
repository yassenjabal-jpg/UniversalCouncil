# Universal Council Agent Runtime Bake-off — Phase 2 Decision Quality

Date: 2026-10-13
Provider: local Ollama on standard public GitHub-hosted runners
Model: qwen3:4b-instruct
Financial cost: USD 0

## Runtime results

| Runtime | Score | Correctness | Blocker F1 | Routing | Dissent | Desktop | Eligible |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 0.4420 | 0.4375 | 0.2250 | 0.1750 | 0.3125 | 0.9000 | False |
| microsoft_agent_framework | 0.2300 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.9000 | False |
| openai_agents | 0.7543 | 0.9375 | 0.4188 | 0.4799 | 0.6250 | 0.9000 | False |

## Decision

State: NO_WINNER
Winner: None
Reason: No runtime satisfied live-decision, mechanics, and policy gates.

The decision-quality run is not allowed to select a final runtime until the YASSIN desktop execution gate reaches 1.0.

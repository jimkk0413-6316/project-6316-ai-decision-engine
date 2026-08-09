# Source Mapping

This repository was prepared from the 04 August 2026 Project 6316 / XAUUSD Golden Sniper V7.9P-TSR-R2 master specification.

| Public module | Source concept |
|---|---|
| `boundary_reference.py` | B1 boundary hierarchy, Pivot High/Low and Donchian reference audit, scan-time input contract, regression logic |
| `adaptive_buffer.py` | R2 dynamic/adaptive buffer and spread realism patches |
| `guardrails.py` | R2 provisional risk ceiling, provisional circuit breaker, daily loss circuit, Micro expiry, psychological-level ranking, manual OCO exposure |
| `oco.py` | R2 OCO preference reinforcement and equal-ranking philosophy |
| `tests/` | Public regression checks derived from the specification's encoded-test approach |

## Deliberate non-implementation note

The R2 TP1 partial-management paragraph states that **80%** is closed at TP1 while the **remaining 30%** may run. Those percentages sum to 110%, so this public repository does **not** silently guess the intended allocation. The rule is excluded until the written specification is reconciled.

This is intentional: rule-constrained systems should surface specification conflicts rather than invent a correction.

# Public Architecture

The public portfolio exposes only a small, inspectable slice of the full Project 6316 system.

```text
Market snapshot / observed values
            |
            v
+--------------------------+
| Structural interpretation|   <- private / human+AI supplied
+--------------------------+
            |
            v
+--------------------------+
| Boundary Reference Audit |
| Pivot HL + Donchian      |
+--------------------------+
            |
            v
+--------------------------+
| Adaptive Buffer          |
| ATR + RVOL + spread      |
+--------------------------+
            |
            v
+--------------------------+
| Candidate legality       |   <- full production search is private
+--------------------------+
       |             |
       v             v
     BUY            SELL
       \             /
        \           /
         v         v
       +-------------+
       | OCO policy  |
       +-------------+
              |
              v
       +-------------+
       | Guardrails  |
       | risk/safety |
       +-------------+
              |
              v
       Research output only
```

## Why this structure matters

The architecture separates three questions that are often mixed together in discretionary AI workflows:

1. **What was observed?**
2. **Is a candidate structurally legal?**
3. **Is it safe to expose capital to it?**

Keeping these domains separate makes rule violations easier to diagnose and regression-test.

# Project 6316 - AI-Assisted Rule-Constrained Financial Decision Engine

**Author:** Wong Keng Keong  
**Status:** Academic / research portfolio prototype  
**Domain:** AI-assisted decision systems, FinTech, quantitative risk governance  
**Reference instrument:** XAUUSD (research context only)

## Overview

Project 6316 is an experimental framework for studying how a large language model can be constrained by explicit rules when making decisions under uncertainty.

The original project grew from repeated XAUUSD market-analysis experiments. Its central research question is broader than trading:

> Can explicit state, deterministic boundary references, volatility-aware rules, risk constraints and regression testing reduce inconsistent AI interpretation?

This public repository contains a **sanitised academic subset** of the project. It demonstrates the architecture and selected rule implementations without publishing the complete production instruction pack or broker-execution workflow.

## What is included

- `boundary_reference.py` - deterministic audit of price-structure boundaries against confirmed Pivot High/Low and Donchian references.
- `adaptive_buffer.py` - volatility / relative-volume adaptive entry-buffer calculation from the current R2 specification.
- `guardrails.py` - selected R2 safety rules represented as pure, testable functions.
- `oco.py` - OCO risk and pair-selection helpers for research simulations.
- `examples/synthetic_scan.py` - synthetic demonstration; no live market or broker connection.
- `tests/` - regression tests for the public modules.

## What is intentionally not published

The public repository does **not** contain:

- the full 62-page live instruction pack;
- complete live candidate-search and ranking logic;
- proprietary case-study memory / decision prompts;
- broker credentials, API keys, account information or order-routing code;
- real customer, broker or private conversation data;
- claims of profitability or a deployable automated trading system.

## Design principles represented here

1. **Structure remains controlling.** Indicators are references, not automatic signals.
2. **Observed inputs must not be invented.** Missing inputs are explicitly represented.
3. **Adaptive rather than fixed execution parameters.** The current R2 buffer expands with relative volume within defined bounds.
4. **Two-sided decision architecture.** When two legal paths exist, OCO logic lets price resolve direction rather than forcing a discretionary forecast.
5. **Capital-protection guardrails.** Spread, daily-loss and OCO exposure checks are modelled separately from structural legality.
6. **Regression testing.** Rule changes should be testable and version-controlled.

## AI-assisted development disclosure

The project requirements, trading-domain rules, iterative test cases and system architecture were directed by **Wong Keng Keong**. Python implementation and documentation were developed with AI-assisted coding and then checked against the written specification and regression tests.

This repository is therefore presented as evidence of **AI tool literacy, system design, rule engineering and validation**, not as evidence that the author manually wrote every line of code without assistance.

## Quick start

Requires Python 3.11+ and uses only the Python standard library.

```bash
python -m unittest discover -s tests -v
python examples/synthetic_scan.py
```

## Research directions

The next empirical stage is intended to examine questions such as:

- whether adaptive entry buffers reduce low-quality trigger events;
- whether two-sided OCO boards behave differently from one-sided selections;
- how often AI models disagree when supplied with the same market snapshot;
- whether deterministic boundary references reduce cross-model interpretation variance;
- the effect of latency and missing data on rule compliance.

## Important limitation

This repository is a research demonstration, **not financial advice, not a performance claim, and not a production trading bot**. The underlying specification explicitly treats replay and controlled live testing as necessary validation rather than assuming profitability.

## Repository scope

See [`docs/public_scope.md`](docs/public_scope.md) and [`docs/source_mapping.md`](docs/source_mapping.md) for the boundary between the public portfolio code and the private production specification.

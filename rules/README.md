# Rule Governance System

This directory contains the AE-OS rule governance structure.

## Directory Structure

```
rules/
├── global/         # Active global rules (production-ready)
├── candidates/    # Candidate rules (from analysis)
└── deprecated/    # Deprecated rules (phased out)
```

## Rule Metadata

All rules MUST include:

| Field | Type | Description |
|-------|------|-------------|
| version | string | Semantic version (e.g., "1.0.0") |
| status | string | candidate | global | deprecated |
| confidence_score | float | 0.0-1.0, rule reliability |
| impact_score | int | 0-10, business impact |
| false_positive_rate | float | 0-100%, false alarm rate |
| created | date | Rule creation date |
| last_triggered | date | Last time rule was triggered |

## Rule Lifecycle

```
candidate → global → deprecated
```

1. **Candidate**: Generated from error analysis, needs review
2. **Global**: Approved and enforced in production
3. **Deprecated**: Phased out, kept for reference

## Staleness Rules

- 6 months without trigger → auto-mark as `stale`
- false_positive_rate > 30% → mark for `review`

## Adding New Rules

1. Run: `opencode-evolve analyze`
2. Review candidate rules in `rules/candidates/`
3. Update metadata (confidence_score, impact_score)
4. Move to `rules/global/` when approved

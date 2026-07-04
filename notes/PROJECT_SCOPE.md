# LAIP Reproduction — Project Scope

Paper: Gelpí, Xue & Cunningham (2025), arXiv:2507.03682.

## Confirmed coverage

| Section | Status | Notes |
|---|---|---|
| Study 1 (Restaurants, 20 hypotheses) | Included | 2 trajectories: Japanese Open, Japanese Closed |
| Study 2 (Restaurants, 6 hypotheses, Optimal Model) | Included | 10 trajectories, Appendix A.2 |
| Section 4.5 (Carol/Alice, open-ended) | Included | 4 scenes, qualitative only |
| MMToM-QA (Section 4.4) | Excluded | Would require reimplementing BIP-ALM etc. |

## Model configurations

| Configuration | Study 1 | Study 2 | 4.5 |
|---|---|---|---|
| LAIP (Full) | Yes | Yes | Yes |
| Zero-shot baseline | Yes | Yes | Yes |
| Generic CoT | Yes | Yes | Yes |
| Optimal Model (analytic, no LLM) | — | Yes | — |

## LLMs (sequenced)

1. **First pass:** GPT-4o-mini only, all runs, via OpenAI Batch API.
   Validate against the paper's published numbers before proceeding.
2. **Then:** Claude Haiku 4.5 as a generalization test, via Anthropic Batch API,
   reusing the identical harness so model is the only variable.

`batch_client.py` is built with a provider-agnostic interface now so step 2 is
a drop-in adapter, not a rewrite — even though only OpenAI is wired up first.

## Cost control
- Batch API (~50% off) for all offline runs
- Pilot (1 trajectory x 2 runs) before any full run, to measure real cost/run
- Raw responses logged to data/raw_responses/ so parsing bugs never cost re-runs
- Fixed + logged temperature and seed per call
- Budget target: ~$3–7 for the GPT-4o-mini first pass

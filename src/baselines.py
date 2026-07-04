"""
baselines.py
============

Comparison configurations against LAIP:
  - Zero-shot baseline: ask the LLM directly for the posterior, no scaffolding
  - Generic CoT: "think step by step" then answer, no inverse-planning structure

These share the same prompt-plumbing and parsing as laip.py so the ONLY
variable across conditions is the reasoning structure, not the harness.
"""

# TODO: implement zero-shot and generic CoT configurations

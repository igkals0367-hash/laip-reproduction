"""
batch_client.py
===============

Provider-agnostic wrapper around batch LLM inference.

Design note (per project scope): GPT-4o-mini runs FIRST and is validated
against the paper's published numbers. Claude Haiku 4.5 is added afterward as
a generalization test. To make that second step a drop-in rather than a
rewrite, this module defines a provider-agnostic `BatchClient` interface. Only
the OpenAI adapter is implemented in the first pass; the Anthropic adapter is
a stub to be filled in once GPT-4o-mini results are confirmed.

Both providers offer a Batch API at ~50% of synchronous cost, which is the
primary cost-control lever for this reproduction.

Responsibilities:
  - Assemble batch request files (one request per hypothesis/likelihood call)
  - Submit, poll, and retrieve batch results
  - Persist EVERY raw response to data/raw_responses/ before parsing, so that
    parsing bugs never require re-paying for API calls
  - Record token counts + running cost estimate per batch
"""

from abc import ABC, abstractmethod


class BatchClient(ABC):
    """Provider-agnostic batch inference interface."""

    @abstractmethod
    def submit_batch(self, requests, batch_name):
        """Submit a list of prompt requests; return a batch handle/id."""
        raise NotImplementedError

    @abstractmethod
    def poll(self, batch_id):
        """Return batch status (pending / complete / failed)."""
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, batch_id):
        """Fetch completed results; persist raw responses to disk."""
        raise NotImplementedError


class OpenAIBatchClient(BatchClient):
    """OpenAI Batch API adapter. Implemented in the first pass (GPT-4o-mini)."""
    # TODO: implement submit/poll/retrieve against OpenAI Batch API
    pass


class AnthropicBatchClient(BatchClient):
    """Anthropic Message Batches adapter. STUB — wire up after GPT-4o-mini
    results are validated, for the Claude Haiku 4.5 generalization test."""
    # TODO: implement once first model is validated
    pass

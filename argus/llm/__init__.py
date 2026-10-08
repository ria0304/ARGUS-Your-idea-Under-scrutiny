"""LLM integration module for ARGUS."""

from argus.llm.nemotron import call_nemotron, call_nemotron_structured, NemotronConfig

__all__ = ["call_nemotron", "call_nemotron_structured", "NemotronConfig"]
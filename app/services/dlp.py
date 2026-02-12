"""
AegisShare — DLP (Data Loss Prevention) Service

Uses Microsoft Presidio + spaCy to detect personally identifiable
information (PII) in free-form text.
"""

from __future__ import annotations

import spacy
from presidio_analyzer import AnalyzerEngine

# Load the spaCy language model once at module level.
# Make sure to run:  python -m spacy download en_core_web_lg
_nlp = spacy.load("en_core_web_lg")
_analyzer = AnalyzerEngine()

# Findings with a confidence score below this threshold are ignored.
CONFIDENCE_THRESHOLD: float = 0.4


def analyze_text(text: str) -> list[dict]:
    """Scan *text* for PII entities and return a list of findings.

    Each finding is a dict with keys:
    ``tipo``, ``confianza``, ``inicio``, ``fin``.
    """
    results = _analyzer.analyze(text=text, language="en")

    return [
        {
            "tipo": res.entity_type,
            "confianza": round(res.score, 2),
            "inicio": res.start,
            "fin": res.end,
        }
        for res in results
    ]


def is_safe(text: str) -> tuple[bool, list[dict]]:
    """Determine whether *text* is free of high-confidence PII.

    Returns:
        A two-element tuple ``(safe, risks)`` where *safe* is ``True``
        when no finding exceeds ``CONFIDENCE_THRESHOLD``, and *risks* is
        the list of flagged findings.
    """
    findings = analyze_text(text)
    risks = [f for f in findings if f["confianza"] > CONFIDENCE_THRESHOLD]
    return len(risks) == 0, risks
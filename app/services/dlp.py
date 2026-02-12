"""
AegisShare — DLP (Data Loss Prevention) Service

Uses Microsoft Presidio + spaCy to detect personally identifiable
information (PII) in free-form text.
Supports configurable policies loaded from the database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import spacy
from presidio_analyzer import AnalyzerEngine

if TYPE_CHECKING:
    from ..models import DlpPolicy

# Load the spaCy language model once at module level.
# Make sure to run:  python -m spacy download en_core_web_lg
_nlp = spacy.load("en_core_web_lg")
_analyzer = AnalyzerEngine()

# Default threshold used when no policies are configured.
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.4


def analyze_text(text: str) -> list[dict]:
    """Scan *text* for PII entities and return a list of findings.

    Each finding is a dict with keys:
    ``entity_type``, ``confidence``, ``start``, ``end``.
    """
    results = _analyzer.analyze(text=text, language="en")

    return [
        {
            "entity_type": res.entity_type,
            "confidence": round(res.score, 2),
            "start": res.start,
            "end": res.end,
        }
        for res in results
    ]


def analyze_with_policies(
    text: str,
    policies: list[DlpPolicy] | None = None,
) -> tuple[bool, list[dict], str]:
    """Analyze text using database-driven DLP policies.

    Args:
        text:     The text content to analyze.
        policies: Active ``DlpPolicy`` rows from the database.
                  If empty/None, falls back to the default threshold.

    Returns:
        A three-element tuple ``(is_safe, risks, risk_level)`` where:
        - *is_safe*:    ``True`` if no blocking findings exist.
        - *risks*:      List of findings that matched a policy.
        - *risk_level*: Overall risk classification string.
    """
    findings = analyze_text(text)

    if not findings:
        return True, [], "none"

    # Build a lookup: entity_type -> policy
    policy_map: dict[str, DlpPolicy] = {}
    if policies:
        for p in policies:
            policy_map[p.entity_type] = p

    risks: list[dict] = []
    has_block = False

    for finding in findings:
        entity = finding["entity_type"]
        confidence = finding["confidence"]

        policy = policy_map.get(entity)

        if policy:
            # Skip entities whose policy action is "ignore"
            if policy.action == "ignore":
                continue
            # Skip findings below the policy's confidence threshold
            if confidence < policy.min_confidence:
                continue

            finding["action"] = policy.action
            finding["policy_name"] = policy.display_name
            risks.append(finding)

            if policy.action == "block":
                has_block = True
        else:
            # No specific policy — use default threshold
            if confidence > DEFAULT_CONFIDENCE_THRESHOLD:
                finding["action"] = "block"
                finding["policy_name"] = entity
                risks.append(finding)
                has_block = True

    # Determine risk level based on findings
    risk_level = _calculate_risk_level(risks)
    is_safe = not has_block

    return is_safe, risks, risk_level


def _calculate_risk_level(risks: list[dict]) -> str:
    """Classify the overall risk based on the number and confidence of findings."""
    if not risks:
        return "none"

    max_confidence = max(r["confidence"] for r in risks)
    count = len(risks)

    if count >= 5 or max_confidence >= 0.95:
        return "critical"
    if count >= 3 or max_confidence >= 0.85:
        return "high"
    if count >= 2 or max_confidence >= 0.7:
        return "medium"
    return "low"
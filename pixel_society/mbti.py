"""Utilities and presets for MBTI personalities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MBTIPersonality:
    """Represents a personality archetype used to seed an agent."""

    code: str
    description: str
    trait_modifiers: Dict[str, float]


# Basic trait keys used across the simulation.
TRAIT_KEYS = [
    "sociability",
    "creativity",
    "organization",
    "empathy",
    "rationality",
    "ambition",
]


def _make_profile(
    code: str,
    *,
    sociability: float,
    creativity: float,
    organization: float,
    empathy: float,
    rationality: float,
    ambition: float,
    description: str,
) -> MBTIPersonality:
    return MBTIPersonality(
        code=code,
        description=description,
        trait_modifiers={
            "sociability": sociability,
            "creativity": creativity,
            "organization": organization,
            "empathy": empathy,
            "rationality": rationality,
            "ambition": ambition,
        },
    )


# A curated subset of MBTI profiles. The values roughly represent the strength of
# the trait compared to a neutral baseline (0.0). Positive values emphasize the
# trait while negative values deemphasize it.
MBTI_PROFILES: Dict[str, MBTIPersonality] = {
    "INTJ": _make_profile(
        "INTJ",
        sociability=-0.2,
        creativity=0.5,
        organization=0.4,
        empathy=-0.1,
        rationality=0.6,
        ambition=0.5,
        description="Strategic mastermind focused on long-term planning and innovation.",
    ),
    "INFP": _make_profile(
        "INFP",
        sociability=0.1,
        creativity=0.6,
        organization=-0.2,
        empathy=0.7,
        rationality=-0.1,
        ambition=0.2,
        description="Idealistic dreamer driven by values and relationships.",
    ),
    "ENTP": _make_profile(
        "ENTP",
        sociability=0.5,
        creativity=0.7,
        organization=-0.3,
        empathy=0.1,
        rationality=0.2,
        ambition=0.4,
        description="Energetic innovator who thrives on debate and new possibilities.",
    ),
    "ESTJ": _make_profile(
        "ESTJ",
        sociability=0.2,
        creativity=-0.2,
        organization=0.7,
        empathy=-0.1,
        rationality=0.4,
        ambition=0.6,
        description="Efficient organizer focused on structure, tradition and leadership.",
    ),
    "ESFP": _make_profile(
        "ESFP",
        sociability=0.7,
        creativity=0.3,
        organization=-0.3,
        empathy=0.5,
        rationality=-0.2,
        ambition=0.2,
        description="Vibrant performer who seeks excitement and social connection.",
    ),
    "ISFJ": _make_profile(
        "ISFJ",
        sociability=-0.1,
        creativity=-0.1,
        organization=0.6,
        empathy=0.6,
        rationality=0.1,
        ambition=-0.1,
        description="Loyal caretaker prioritizing harmony and practical support.",
    ),
    "ENTJ": _make_profile(
        "ENTJ",
        sociability=0.4,
        creativity=0.2,
        organization=0.6,
        empathy=-0.2,
        rationality=0.5,
        ambition=0.8,
        description="Commanding leader focused on achievement and strategic execution.",
    ),
    "ISTP": _make_profile(
        "ISTP",
        sociability=-0.2,
        creativity=0.3,
        organization=-0.1,
        empathy=-0.2,
        rationality=0.4,
        ambition=0.1,
        description="Curious problem-solver who prefers hands-on experimentation.",
    ),
}


def personality_for(code: str) -> MBTIPersonality:
    """Return a :class:`MBTIPersonality` by code.

    The lookup is case-insensitive and falls back to a neutral personality if no
    predefined profile is found.
    """

    normalized = code.upper()
    if normalized in MBTI_PROFILES:
        return MBTI_PROFILES[normalized]

    neutral = {key: 0.0 for key in TRAIT_KEYS}
    return MBTIPersonality(
        code=normalized,
        description="Custom personality",
        trait_modifiers=neutral,
    )

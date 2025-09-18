"""Core agent models used in the PixelSociety simulation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from . import mbti
from .tasks import Task, TaskFeedback


@dataclass
class EmotionState:
    """Tracks the emotional well-being of an agent."""

    happiness: float = 0.5
    stress: float = 0.2
    energy: float = 0.7

    def clamp(self) -> None:
        self.happiness = max(0.0, min(1.0, self.happiness))
        self.stress = max(0.0, min(1.0, self.stress))
        self.energy = max(0.0, min(1.0, self.energy))


@dataclass
class Relationship:
    """Represents the connection between two agents."""

    other: str
    closeness: float = 0.1
    trust: float = 0.1
    sentiment: str = "neutral"

    def adjust(self, *, closeness: float = 0.0, trust: float = 0.0) -> None:
        self.closeness = max(0.0, min(1.0, self.closeness + closeness))
        self.trust = max(0.0, min(1.0, self.trust + trust))
        if self.trust > 0.7 and self.closeness > 0.6:
            self.sentiment = "ally"
        elif self.trust < 0.3 and self.closeness < 0.3:
            self.sentiment = "rival"
        else:
            self.sentiment = "neutral"


@dataclass
class Agent:
    """AI agent controlled by the simulation."""

    name: str
    mbti_code: str
    prompt: Optional[str] = None
    occupation: str = "Unassigned"
    skills: Dict[str, float] = field(default_factory=dict)
    resources: Dict[str, float] = field(default_factory=lambda: {"money": 100.0, "time": 40.0})
    motivations: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)
    emotion: EmotionState = field(default_factory=EmotionState)

    def __post_init__(self) -> None:
        personality = mbti.personality_for(self.mbti_code)
        self.personality = personality
        # Base traits start with MBTI modifiers and can be tweaked via prompts.
        self.traits: Dict[str, float] = dict(personality.trait_modifiers)

    # --- customization utilities -------------------------------------------------
    def customize(self, *, trait_overrides: Optional[Dict[str, float]] = None, motivations: Optional[Iterable[str]] = None, values: Optional[Iterable[str]] = None) -> None:
        """Apply prompt-based customization to the agent."""

        if trait_overrides:
            for key, delta in trait_overrides.items():
                if key in mbti.TRAIT_KEYS:
                    self.traits[key] = max(-1.0, min(1.0, self.traits.get(key, 0.0) + delta))
        if motivations:
            self.motivations.extend(motivations)
        if values:
            self.values.extend(values)

    # --- relationship management --------------------------------------------------
    def get_relationship(self, other: str) -> Relationship:
        if other not in self.relationships:
            self.relationships[other] = Relationship(other=other)
        return self.relationships[other]

    def influence_relationship(self, other: str, affinity: float) -> None:
        relationship = self.get_relationship(other)
        relationship.adjust(
            closeness=0.1 * affinity,
            trust=0.1 * affinity,
        )

    # --- resource and skill progression ------------------------------------------
    def learn_skill(self, skill: str, effort: float) -> None:
        baseline = 0.5 + self.traits.get("creativity", 0) * 0.2
        self.skills[skill] = min(1.0, self.skills.get(skill, 0.0) + effort * baseline)

    def adjust_resources(self, *, money: float = 0.0, time: float = 0.0) -> None:
        self.resources["money"] = max(0.0, self.resources.get("money", 0.0) + money)
        self.resources["time"] = max(0.0, self.resources.get("time", 0.0) + time)

    # --- emotional adjustments ----------------------------------------------------
    def adjust_emotion(self, *, happiness: float = 0.0, stress: float = 0.0, energy: float = 0.0) -> None:
        self.emotion.happiness += happiness
        self.emotion.stress += stress
        self.emotion.energy += energy
        self.emotion.clamp()

    # --- task processing ----------------------------------------------------------
    def assign_task(self, task: Task) -> None:
        self.tasks.append(task)

    def advance_tasks(self, world_state: "World") -> List[TaskFeedback]:
        feedback: List[TaskFeedback] = []
        remaining_tasks: List[Task] = []
        for task in self.tasks:
            fb = task.advance(self, world_state)
            feedback.append(fb)
            if not task.completed:
                remaining_tasks.append(task)
        self.tasks = remaining_tasks
        return feedback

    # --- tick update --------------------------------------------------------------
    def tick(self, world_state: "World") -> List[TaskFeedback]:
        """Update the agent for a single simulation step."""

        # Base mood adjustments depending on stress and available time.
        if self.resources.get("time", 0.0) < 10:
            self.adjust_emotion(stress=0.05)
        else:
            self.adjust_emotion(happiness=0.02, stress=-0.02)

        # Agents naturally regenerate a bit of time each tick.
        self.adjust_resources(time=5.0)

        # Progress tasks and record feedback.
        feedback = self.advance_tasks(world_state)

        # Slightly decay relationship closeness unless maintained.
        for rel in self.relationships.values():
            rel.adjust(closeness=-0.02, trust=-0.01)

        return feedback

"""Task and goal management."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

if False:  # pragma: no cover - circular import hints only for type checking
    from .agents import Agent
    from .world import World


@dataclass
class TaskFeedback:
    """Result of progressing a task for a single tick."""

    task_name: str
    progress_delta: float
    completed: bool
    message: str


ProgressFunction = Callable[["Agent", "World"], float]


@dataclass
class Task:
    """Represents a goal set for an agent."""

    name: str
    description: str
    required_progress: float = 1.0
    difficulty: float = 1.0
    progress_function: Optional[ProgressFunction] = None
    resources_required: Dict[str, float] = field(default_factory=dict)
    completed: bool = False
    progress: float = 0.0

    def advance(self, agent: "Agent", world: "World") -> TaskFeedback:
        if self.completed:
            return TaskFeedback(self.name, 0.0, True, "Task already completed.")

        # Check resources
        for resource, amount in self.resources_required.items():
            if agent.resources.get(resource, 0.0) < amount:
                agent.adjust_emotion(stress=0.05)
                return TaskFeedback(
                    self.name,
                    0.0,
                    False,
                    f"Insufficient {resource} to progress {self.name}.",
                )

        for resource, amount in self.resources_required.items():
            agent.adjust_resources(**{resource: -amount})

        if self.progress_function:
            delta = self.progress_function(agent, world)
        else:
            # Generic progress uses traits and skill synergy
            creativity = agent.traits.get("creativity", 0.0)
            organization = agent.traits.get("organization", 0.0)
            skill_bonus = max(agent.skills.values()) if agent.skills else 0.1
            delta = max(0.05, 0.2 + creativity * 0.1 + organization * 0.05 + skill_bonus * 0.2)

        delta /= max(0.5, self.difficulty)
        self.progress += delta
        message = f"Progressed {self.name} by {delta:.2f}"

        if self.progress >= self.required_progress:
            self.completed = True
            agent.adjust_emotion(happiness=0.1, stress=-0.1)
            message = f"Completed task {self.name}!"

        return TaskFeedback(self.name, delta, self.completed, message)

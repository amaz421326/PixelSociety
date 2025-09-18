"""World and agent events."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Optional

if False:  # pragma: no cover - typing hints only
    from .agents import Agent
    from .world import World


WorldEffect = Callable[["World"], None]
AgentEffect = Callable[["Agent", "World"], None]


@dataclass
class Event:
    """A world event that can impact agents and the environment."""

    name: str
    description: str
    world_effect: Optional[WorldEffect] = None
    agent_effects: Iterable[AgentEffect] = field(default_factory=list)

    def apply(self, world: "World", agents: Iterable["Agent"]) -> None:
        if self.world_effect:
            self.world_effect(world)
        for effect in self.agent_effects:
            for agent in agents:
                effect(agent, world)
        world.record_event(self.description)

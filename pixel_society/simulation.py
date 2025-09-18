"""Main simulation loop and utilities."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from .agents import Agent
from .events import Event
from .reports import generate_agent_report, generate_world_report
from .world import Region, World


@dataclass
class ScheduledEvent:
    tick: int
    event: Event


@dataclass
class SimulationResult:
    tick: int
    feedback: Dict[str, List[str]]
    events: List[str]


class Simulation:
    """Coordinates the world, agents and events."""

    def __init__(self, world: World, *, seed: Optional[int] = None) -> None:
        self.world = world
        self.seed = seed or random.randint(0, 99999)
        self.random = random.Random(self.seed)
        self.agents: Dict[str, Agent] = {}
        self.scheduled_events: List[ScheduledEvent] = []
        self.history: List[SimulationResult] = []

    # ------------------------------------------------------------------ management
    def add_agent(self, agent: Agent, *, region: Optional[str] = None) -> None:
        self.agents[agent.name] = agent
        if region:
            self.world.place_agent(agent.name, region)

    def add_region(self, name: str, *, resources: Optional[Dict[str, float]] = None, culture_focus: str = "urban") -> Region:
        region = Region(name=name, resources=resources or {"food": 50, "energy": 30}, culture_focus=culture_focus)
        self.world.add_region(region)
        return region

    def schedule_event(self, event: Event, *, in_ticks: int = 0) -> None:
        trigger_tick = self.world.tick_count + in_ticks
        self.scheduled_events.append(ScheduledEvent(tick=trigger_tick, event=event))

    # ---------------------------------------------------------------------- helpers
    def _select_pairs(self) -> Iterable[Tuple[Agent, Agent]]:
        agents = list(self.agents.values())
        self.random.shuffle(agents)
        for i in range(0, len(agents) - 1, 2):
            yield agents[i], agents[i + 1]

    def _handle_interaction(self, a: Agent, b: Agent) -> None:
        affinity = 0.1
        affinity += 0.1 * (1 - abs(a.traits.get("sociability", 0) - b.traits.get("sociability", 0)))
        affinity += 0.05 * (1 - abs(a.traits.get("empathy", 0) - b.traits.get("empathy", 0)))
        affinity -= 0.05 * abs(a.traits.get("organization", 0) - b.traits.get("organization", 0))
        affinity = max(-1.0, min(1.0, affinity))
        a.influence_relationship(b.name, affinity)
        b.influence_relationship(a.name, affinity)
        if affinity > 0:
            a.adjust_emotion(happiness=0.02)
            b.adjust_emotion(happiness=0.02)
        else:
            a.adjust_emotion(stress=0.02)
            b.adjust_emotion(stress=0.02)

    def _apply_world_feedback(self) -> None:
        if not self.agents:
            return
        avg_ambition = sum(agent.traits.get("ambition", 0.0) for agent in self.agents.values()) / len(self.agents)
        avg_happiness = sum(agent.emotion.happiness for agent in self.agents.values()) / len(self.agents)
        avg_stress = sum(agent.emotion.stress for agent in self.agents.values()) / len(self.agents)
        economy_delta = 0.02 * avg_ambition - 0.01 * avg_stress
        culture_delta = 0.01 * avg_happiness
        stability_delta = 0.02 * avg_happiness - 0.015 * avg_stress
        self.world.adjust_global_state(economy=economy_delta, culture=culture_delta, stability=stability_delta)

    def _trigger_events(self) -> List[str]:
        triggered: List[str] = []
        pending: List[ScheduledEvent] = []
        for scheduled in self.scheduled_events:
            if scheduled.tick <= self.world.tick_count:
                scheduled.event.apply(self.world, self.agents.values())
                triggered.append(scheduled.event.description)
            else:
                pending.append(scheduled)
        self.scheduled_events = pending
        return triggered

    # -------------------------------------------------------------------------- tick
    def tick(self) -> SimulationResult:
        self.world.tick()
        triggered_events = self._trigger_events()

        feedback: Dict[str, List[str]] = {}
        for agent in self.agents.values():
            task_feedback = agent.tick(self.world)
            feedback[agent.name] = [fb.message for fb in task_feedback]

        # Social interactions
        for a, b in self._select_pairs():
            self._handle_interaction(a, b)

        self._apply_world_feedback()

        result = SimulationResult(self.world.tick_count, feedback, triggered_events)
        self.history.append(result)
        return result

    # -------------------------------------------------------------------------- loop
    def run(self, steps: int) -> List[SimulationResult]:
        return [self.tick() for _ in range(steps)]

    # ------------------------------------------------------------------------ reports
    def agent_reports(self) -> Dict[str, str]:
        return {name: generate_agent_report(agent) for name, agent in self.agents.items()}

    def world_report(self) -> str:
        return generate_world_report(self.world, self.agents.values())

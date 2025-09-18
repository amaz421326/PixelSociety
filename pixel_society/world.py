"""World state and regions for the PixelSociety simulation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Region:
    """A location within the world that agents can inhabit."""

    name: str
    resources: Dict[str, float]
    culture_focus: str
    population: int = 0

    def adjust_resource(self, resource: str, delta: float) -> None:
        self.resources[resource] = max(0.0, self.resources.get(resource, 0.0) + delta)


@dataclass
class World:
    """Global world state shared across all agents."""

    name: str
    economy: float = 0.5
    culture: float = 0.5
    stability: float = 0.5
    regions: Dict[str, Region] = field(default_factory=dict)
    agent_locations: Dict[str, str] = field(default_factory=dict)
    event_log: List[str] = field(default_factory=list)
    tick_count: int = 0

    def add_region(self, region: Region) -> None:
        self.regions[region.name] = region

    def place_agent(self, agent_name: str, region_name: str) -> None:
        self.agent_locations[agent_name] = region_name
        if region_name in self.regions:
            self.regions[region_name].population += 1

    def relocate_agent(self, agent_name: str, region_name: str) -> None:
        previous = self.agent_locations.get(agent_name)
        if previous and previous in self.regions:
            self.regions[previous].population = max(0, self.regions[previous].population - 1)
        self.place_agent(agent_name, region_name)

    def record_event(self, description: str) -> None:
        entry = f"[Tick {self.tick_count}] {description}"
        self.event_log.append(entry)

    def adjust_global_state(self, *, economy: float = 0.0, culture: float = 0.0, stability: float = 0.0) -> None:
        self.economy = max(0.0, min(1.0, self.economy + economy))
        self.culture = max(0.0, min(1.0, self.culture + culture))
        self.stability = max(0.0, min(1.0, self.stability + stability))

    def region_for_agent(self, agent_name: str) -> Optional[Region]:
        location = self.agent_locations.get(agent_name)
        if location:
            return self.regions.get(location)
        return None

    def tick(self) -> None:
        self.tick_count += 1

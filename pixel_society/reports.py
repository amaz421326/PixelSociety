"""Reporting utilities for agents and the world state."""
from __future__ import annotations

from typing import Iterable, List

from .agents import Agent
from .world import World


def _format_percentage(value: float) -> str:
    return f"{value * 100:.0f}%"


def generate_agent_report(agent: Agent) -> str:
    lines: List[str] = [
        f"Agent {agent.name} ({agent.personality.code})",
        f"Occupation: {agent.occupation}",
        f"Motivations: {', '.join(agent.motivations) or 'None'}",
        f"Values: {', '.join(agent.values) or 'None'}",
        "Traits:",
    ]
    for trait, value in agent.traits.items():
        lines.append(f"  - {trait}: {value:+.2f}")
    lines.append("Skills:")
    if agent.skills:
        for skill, level in agent.skills.items():
            lines.append(f"  - {skill}: {_format_percentage(level)}")
    else:
        lines.append("  - None yet")
    lines.append("Resources:")
    for resource, amount in agent.resources.items():
        lines.append(f"  - {resource}: {amount:.1f}")
    lines.append("Relationships:")
    if agent.relationships:
        for relation in agent.relationships.values():
            lines.append(
                f"  - {relation.other}: closeness {_format_percentage(relation.closeness)}, trust {_format_percentage(relation.trust)} ({relation.sentiment})"
            )
    else:
        lines.append("  - None yet")
    lines.append(
        f"Emotion: happiness {_format_percentage(agent.emotion.happiness)}, stress {_format_percentage(agent.emotion.stress)}, energy {_format_percentage(agent.emotion.energy)}"
    )
    return "\n".join(lines)


def generate_world_report(world: World, agents: Iterable[Agent]) -> str:
    lines = [
        f"World: {world.name}",
        f"Economy: {_format_percentage(world.economy)} | Culture: {_format_percentage(world.culture)} | Stability: {_format_percentage(world.stability)}",
        "Regions:",
    ]
    for region in world.regions.values():
        resource_summary = ", ".join(f"{name}: {amount:.0f}" for name, amount in region.resources.items())
        lines.append(
            f"  - {region.name} (focus: {region.culture_focus}, population: {region.population}) resources -> {resource_summary}"
        )
    lines.append("Agents:")
    for agent in agents:
        region = world.agent_locations.get(agent.name, "Unknown")
        lines.append(f"  - {agent.name} located in {region}, occupation {agent.occupation}")
    if world.event_log:
        lines.append("Recent events:")
        lines.extend(f"  * {entry}" for entry in world.event_log[-5:])
    return "\n".join(lines)

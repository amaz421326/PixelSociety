"""Reusable scenario setup helpers for PixelSociety."""
from __future__ import annotations

from typing import Optional

from .agents import Agent
from .events import Event
from .simulation import Simulation
from .tasks import Task
from .world import World


def create_base_simulation(*, seed: Optional[int] = 42) -> Simulation:
    """Create a simulation with a preconfigured world but no agents."""

    world = World(name="Neo Arcadia", economy=0.6, culture=0.5, stability=0.7)
    simulation = Simulation(world, seed=seed)

    simulation.add_region(
        "Metropolis",
        resources={"food": 80, "energy": 120, "credits": 60},
        culture_focus="technology",
    )
    simulation.add_region(
        "HarborTown",
        resources={"food": 120, "energy": 40, "credits": 30},
        culture_focus="trade",
    )
    simulation.add_region(
        "GreenFields",
        resources={"food": 160, "energy": 20, "credits": 10},
        culture_focus="agriculture",
    )

    return simulation


def populate_demo_agents(simulation: Simulation) -> None:
    """Populate the provided simulation with the default demo agents."""

    aurora = Agent("Aurora", "INFP", prompt="A compassionate artist seeking social change.")
    aurora.customize(
        trait_overrides={"creativity": 0.3, "empathy": 0.2},
        motivations=["Inspire community"],
        values=["Harmony", "Art"],
    )
    aurora.occupation = "Community Planner"
    aurora.learn_skill("Design", 0.6)
    aurora.assign_task(
        Task("Community Garden", "Establish a sustainable garden in GreenFields", required_progress=2.5)
    )
    simulation.add_agent(aurora, region="GreenFields")

    dex = Agent("Dex", "ESTJ", prompt="A pragmatic entrepreneur driven to optimize society's logistics.")
    dex.customize(
        trait_overrides={"organization": 0.3, "ambition": 0.2},
        motivations=["Grow wealth"],
        values=["Efficiency", "Order"],
    )
    dex.occupation = "Logistics Manager"
    dex.learn_skill("Management", 0.7)
    dex.assign_task(
        Task(
            "Supply Chain",
            "Improve the supply chain between Metropolis and HarborTown",
            required_progress=3.0,
            difficulty=1.5,
            resources_required={"time": 8.0},
        )
    )
    simulation.add_agent(dex, region="Metropolis")

    nova = Agent("Nova", "ENTP", prompt="A futurist technologist experimenting with AI ethics.")
    nova.customize(
        trait_overrides={"creativity": 0.2, "rationality": 0.3},
        motivations=["Innovate AI"],
        values=["Freedom", "Knowledge"],
    )
    nova.occupation = "AI Researcher"
    nova.learn_skill("Engineering", 0.8)
    nova.assign_task(
        Task(
            "Ethical AI Protocol",
            "Design guidelines that balance innovation and social harmony",
            required_progress=2.0,
            difficulty=1.2,
            resources_required={"time": 6.0},
        )
    )
    simulation.add_agent(nova, region="Metropolis")

    def festival_effect(world: World) -> None:
        world.adjust_global_state(culture=0.1, stability=0.05)

    def festival_agent_effect(agent: Agent, _world: World) -> None:
        agent.adjust_emotion(happiness=0.1, stress=-0.05)

    festival = Event(
        name="Harvest Festival",
        description="A joyful harvest festival boosts morale and cultural identity.",
        world_effect=festival_effect,
        agent_effects=[festival_agent_effect],
    )

    simulation.schedule_event(festival, in_ticks=2)


def create_demo_simulation(*, seed: Optional[int] = 42) -> Simulation:
    """Create the default demo simulation with prebuilt agents and events."""

    simulation = create_base_simulation(seed=seed)
    populate_demo_agents(simulation)
    return simulation

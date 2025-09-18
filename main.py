"""Command line entry point demonstrating the PixelSociety simulation."""
from __future__ import annotations

from pixel_society.demo import create_demo_simulation


def main() -> None:
    simulation = create_demo_simulation()
    for _ in range(6):
        result = simulation.tick()
        if result.events:
            print(f"Events triggered on tick {result.tick}: {', '.join(result.events)}")
        for agent_name, feedback in result.feedback.items():
            for line in feedback:
                print(f"[{result.tick}] {agent_name}: {line}")
    print("\nFinal Agent Reports:\n")
    for report in simulation.agent_reports().values():
        print(report)
        print("-" * 40)
    print("World Report:\n")
    print(simulation.world_report())


if __name__ == "__main__":
    main()

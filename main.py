from __future__ import annotations

from datetime import date, timedelta

from models.continuous_task import ContinuousTask
from models.non_continuous_task import NonContinuousTask
from scheduler.planner import Planner


def print_schedule(schedule) -> None:
    if not schedule:
        print("No schedule generated.")
        return

    print("\nGenerated Study Plan")
    print("=" * 24)
    for day in sorted(schedule.keys()):
        items = schedule[day]
        print(f"{day.isoformat()}:")
        for name, hours in items:
            print(f"  - {name}: {hours:.1f} hour(s)")


def demo_tasks(today: date):
    return [
        ContinuousTask(
            name="History Essay",
            estimated_hours=8,
            due_date=today + timedelta(days=6),
            priority=5,
            course="History",
            created_at=today,
        ),
        NonContinuousTask(
            name="Math Worksheet Set",
            estimated_hours=3,
            due_date=today + timedelta(days=2),
            priority=4,
            course="Math",
            created_at=today,
        ),
        ContinuousTask(
            name="Biology Reading Notes",
            estimated_hours=4,
            due_date=today + timedelta(days=5),
            priority=3,
            course="Biology",
            created_at=today,
        ),
    ]


def main() -> None:
    today = date.today()
    tasks = demo_tasks(today)

    daily_availability = {
        0: 2.0,  # Monday
        1: 2.0,
        2: 2.0,
        3: 2.0,
        4: 2.0,
        5: 3.0,  # Saturday
        6: 3.0,  # Sunday
    }

    planner = Planner(daily_availability)
    end_date = max(task.due_date for task in tasks)
    schedule = planner.build_schedule(tasks, start_date=today, end_date=end_date)

    print_schedule(schedule)


if __name__ == "__main__":
    main()

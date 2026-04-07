from __future__ import annotations

from datetime import date

from assignment_tracker import Planner, build_demo_tasks


def print_schedule(schedule) -> None:
    if not schedule:
        print("No schedule generated.")
        return

    print("\nGenerated Study Plan")
    print("=" * 24)
    for day in sorted(schedule.keys()):
        print(f"{day.isoformat()}:")
        for name, hours in schedule[day]:
            print(f"  - {name}: {hours:.1f} hour(s)")


def main() -> None:
    today = date.today()
    tasks = build_demo_tasks(today)

    daily_availability = {
        0: 2.0,
        1: 2.0,
        2: 2.0,
        3: 2.0,
        4: 2.0,
        5: 3.0,
        6: 3.0,
    }

    planner = Planner(daily_availability)
    end_date = max(task.due_date for task in tasks)
    schedule = planner.build_schedule(tasks, start_date=today, end_date=end_date)
    print_schedule(schedule)


if __name__ == "__main__":
    main()

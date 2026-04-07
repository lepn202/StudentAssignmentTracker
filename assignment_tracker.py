from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, Iterable, List, Tuple

Schedule = Dict[date, List[Tuple[str, float]]]


@dataclass
class Task:
    """Base class representing a student assignment task."""

    name: str
    estimated_hours: float
    due_date: date
    priority: int
    course: str
    created_at: date
    completed_hours: float = 0.0
    status: str = field(default="not_started")

    def remaining_hours(self) -> float:
        return max(0.0, self.estimated_hours - self.completed_hours)

    def days_until_due(self, today: date) -> int:
        return (self.due_date - today).days

    def is_overdue(self, today: date) -> bool:
        return self.days_until_due(today) < 0 and not self.is_completed()

    def update_progress(self, hours_done: float) -> None:
        if hours_done <= 0:
            return

        self.completed_hours = min(self.estimated_hours, self.completed_hours + hours_done)
        if self.completed_hours == 0:
            self.status = "not_started"
        elif self.completed_hours < self.estimated_hours:
            self.status = "in_progress"
        else:
            self.status = "completed"

    def is_completed(self) -> bool:
        return self.remaining_hours() == 0.0

    def recommended_daily_chunk(self, days_left: int) -> float:
        if days_left <= 0:
            return self.remaining_hours()
        return self.remaining_hours() / days_left


@dataclass
class ContinuousTask(Task):
    """Task that can be split into multiple study sessions."""

    min_session_hours: float = 0.5
    max_session_hours: float = 2.0

    def recommended_daily_chunk(self, days_left: int) -> float:
        if self.is_completed():
            return 0.0

        if days_left <= 0:
            raw_chunk = self.remaining_hours()
        elif days_left <= 2:
            raw_chunk = self.remaining_hours() / max(1, days_left)
        else:
            raw_chunk = self.remaining_hours() / days_left

        if raw_chunk < self.min_session_hours:
            return min(self.min_session_hours, self.remaining_hours())
        return min(raw_chunk, self.max_session_hours, self.remaining_hours())


@dataclass
class NonContinuousTask(Task):
    """Task that is best completed in one uninterrupted work block."""

    requires_single_block: bool = True

    def recommended_daily_chunk(self, days_left: int) -> float:
        if self.is_completed():
            return 0.0

        if days_left < 0:
            return self.remaining_hours()
        elif days_left == 0:
            return self.remaining_hours()
        else:
            return self.remaining_hours()


class Planner:
    """Creates a schedule of tasks over a date range."""

    def __init__(self, daily_availability: Dict[int, float]):
        self.daily_availability = daily_availability

    def build_schedule(
        self,
        tasks: Iterable[Task],
        start_date: date,
        end_date: date,
    ) -> Schedule:
        schedule: Schedule = defaultdict(list)
        task_list = list(tasks)

        if start_date > end_date:
            return schedule

        task_list.sort(key=lambda t: (t.due_date, -t.priority))

        current_day = start_date
        while current_day <= end_date:
            hours_left = self.daily_availability.get(current_day.weekday(), 0.0)

            for task in task_list:
                if hours_left <= 0:
                    break
                if task.is_completed():
                    continue

                days_left = task.days_until_due(current_day)
                if days_left < 0:
                    continue

                if isinstance(task, NonContinuousTask):
                    needed = task.recommended_daily_chunk(days_left)
                    if needed <= hours_left:
                        schedule[current_day].append((task.name, needed))
                        task.update_progress(needed)
                        hours_left -= needed
                elif isinstance(task, ContinuousTask):
                    chunk = task.recommended_daily_chunk(days_left)
                    assigned = min(chunk, task.remaining_hours(), hours_left)
                    if assigned > 0:
                        schedule[current_day].append((task.name, assigned))
                        task.update_progress(assigned)
                        hours_left -= assigned
                else:
                    chunk = task.recommended_daily_chunk(max(days_left, 1))
                    assigned = min(chunk, task.remaining_hours(), hours_left)
                    if assigned > 0:
                        schedule[current_day].append((task.name, assigned))
                        task.update_progress(assigned)
                        hours_left -= assigned

            current_day += timedelta(days=1)

        return schedule


def schedule_rows(schedule: Schedule) -> List[dict]:
    """Notebook-friendly flat rows for easy DataFrame conversion."""
    rows: List[dict] = []
    for day in sorted(schedule.keys()):
        for task_name, hours in schedule[day]:
            rows.append({"date": day.isoformat(), "task": task_name, "hours": hours})
    return rows


def build_demo_tasks(today: date) -> List[Task]:
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

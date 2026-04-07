from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, Iterable, List, Tuple
from uuid import uuid4

Schedule = Dict[date, List[Tuple[str, float]]]


@dataclass
class Task:
    """Base class representing a student assignment task."""

    name: str  # Public: shown directly to the user in schedules/UI.
    estimated_hours: float  # Public: user-defined planning input.
    due_date: date  # Public: required for schedule ordering.
    priority: int  # Public: user-controlled urgency level.
    course: str  # Public: displayed for context/filtering in UI.
    created_at: date  # Public: useful metadata for display/sorting.

    completed_hours: float = 0.0  # Public: visible progress metric.
    status: str = field(default="not_started")  # Public: shown in UI/workflows.

    _task_id: str = field(default_factory=lambda: uuid4().hex, init=False, repr=False)
    # Private: stable internal identifier not needed in user-facing output.

    _status_history: List[str] = field(default_factory=list, init=False, repr=False)
    # Private: internal audit trail for status transitions.

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

        self._status_history.append(self.status)

    def is_completed(self) -> bool:
        return self.remaining_hours() == 0.0

    def recommended_daily_chunk(self, days_left: int) -> float:
        if days_left <= 0:
            return self.remaining_hours()
        return self.remaining_hours() / days_left


@dataclass
class ContinuousTask(Task):
    """Task that can be split into multiple study sessions."""

    min_session_hours: float = 0.5  # Public: user-configurable session preference.
    max_session_hours: float = 2.0  # Public: user-configurable session cap.

    _chunk_strategy_name: str = field(default="bounded_chunk", init=False, repr=False)
    # Private: internal strategy label for debugging, not user input.

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

    requires_single_block: bool = True  # Public: task behavior visible to planner/UI.

    _block_strategy_name: str = field(default="single_block", init=False, repr=False)
    # Private: internal strategy label for debugging, not user input.

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
        self.daily_availability = daily_availability  # Public: editable by user workflows.
        self._last_generated_schedule_size = 0  # Private: internal telemetry/debug value.

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

        self._last_generated_schedule_size = sum(len(items) for items in schedule.values())
        return schedule


def schedule_rows(schedule: Schedule) -> List[dict]:
    """Flat rows for easy display in notebook or UI tables."""
    rows: List[dict] = []
    for day in sorted(schedule.keys()):
        for task_name, hours in schedule[day]:
            rows.append({"date": day.isoformat(), "task": task_name, "hours": hours})
    return rows

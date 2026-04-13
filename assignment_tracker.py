"""
Core logic and models for the Student Assignment Tracker.
Defines task types (continuous and non-continuous) and a planner for building study schedules.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Iterable, List, Tuple

# Type alias for the study schedule
Schedule = Dict[date, List[Tuple[str, float]]]


@dataclass
class Task:
    """
    Base class for all assignment tasks.
    """
    name: str
    estimated_hours: float
    due_date: date
    priority: int
    course: str
    created_at: date
    completed_hours: float = 0.0
    status: str = "not_started"

    def remaining_hours(self) -> float:
        """
        Returns the number of hours left to complete the task.
        """
        return max(0.0, self.estimated_hours - self.completed_hours)

    def days_until_due(self, today: date) -> int:
        """
        Calculates the number of days from 'today' until the due date.
        """
        return (self.due_date - today).days

    def update_progress(self, hours_done: float) -> None:
        """
        Updates the completed hours and status of the task.
        """
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
        """
        Checks if the task has been finished.
        """
        return self.remaining_hours() == 0.0

    def recommended_daily_chunk(self, days_left: int) -> float:
        """
        Calculates a recommended amount of work for a single day.
        """
        if days_left <= 0:
            return self.remaining_hours()
        return self.remaining_hours() / days_left


@dataclass
class ContinuousTask(Task):
    """
    A task that can be split into multiple smaller study sessions.
    Includes constraints for minimum and maximum session durations.
    """
    min_session_hours: float = 0.5
    max_session_hours: float = 2.0

    def recommended_daily_chunk(self, days_left: int) -> float:
        """
        Calculates a recommended amount of work, respecting session hour constraints.
        """
        if self.is_completed():
            return 0.0

        if days_left <= 0:
            raw_chunk = self.remaining_hours()
        elif days_left <= 2:
            raw_chunk = self.remaining_hours() / max(1, days_left)
        else:
            raw_chunk = self.remaining_hours() / days_left

        # Apply session constraints
        if raw_chunk < self.min_session_hours:
            return min(self.min_session_hours, self.remaining_hours())
        return min(raw_chunk, self.max_session_hours, self.remaining_hours())


@dataclass
class NonContinuousTask(Task):
    """
    A task that is intended to be completed in a single block of time.
    """
    requires_single_block: bool = True

    def recommended_daily_chunk(self, days_left: int) -> float:
        """
        Recommends completing the entire remaining work for non-continuous tasks.
        """
        if self.is_completed():
            return 0.0
        return self.remaining_hours()


class Planner:
    """
    Schedules tasks based on daily availability and task priorities.
    """
    def __init__(self, daily_availability: Dict[int, float]):
        """
        Initializes the Planner with a dictionary mapping weekdays to available hours.
        """
        self.daily_availability = daily_availability

    def build_schedule(self, tasks: Iterable[Task], start_date: date, end_date: date) -> Schedule:
        """
        Generates a day-by-day study schedule.

        Args:
            tasks (Iterable[Task]): The tasks to be scheduled.
            start_date (date): The first day of the schedule.
            end_date (date): The last possible day of the schedule.

        Returns:
            Schedule: A dictionary mapping each date to a list of (task_name, hours) tuples.
        """
        schedule: Schedule = defaultdict(list)
        # Sort tasks by due date (earliest first) and then by priority (highest first)
        task_list = sorted(list(tasks), key=lambda t: (t.due_date, -t.priority))

        if start_date > end_date:
            return schedule

        current_day = start_date
        while current_day <= end_date:
            # Determine available hours for the current day of the week
            hours_left = self.daily_availability.get(current_day.weekday(), 0.0)

            for task in task_list:
                if hours_left <= 0 or task.is_completed():
                    continue

                days_left = task.days_until_due(current_day)
                if days_left < 0:
                    continue

                # Allocate hours based on the task type
                if isinstance(task, NonContinuousTask):
                    needed = task.recommended_daily_chunk(days_left)
                    # Non-continuous tasks are only added if they fit in the remaining time
                    if needed <= hours_left:
                        schedule[current_day].append((task.name, needed))
                        task.update_progress(needed)
                        hours_left -= needed
                elif isinstance(task, ContinuousTask):
                    # Continuous tasks can take a portion of the available time
                    assigned = min(task.recommended_daily_chunk(days_left), task.remaining_hours(), hours_left)
                    if assigned > 0:
                        schedule[current_day].append((task.name, assigned))
                        task.update_progress(assigned)
                        hours_left -= assigned
                else:
                    # Fallback for other potential task types
                    assigned = min(task.recommended_daily_chunk(max(days_left, 1)), task.remaining_hours(), hours_left)
                    if assigned > 0:
                        schedule[current_day].append((task.name, assigned))
                        task.update_progress(assigned)
                        hours_left -= assigned

            current_day += timedelta(days=1)

        return schedule

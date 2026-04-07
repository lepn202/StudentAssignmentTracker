from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, Iterable, List, Tuple

from models.continuous_task import ContinuousTask
from models.non_continuous_task import NonContinuousTask
from models.task import Task

Schedule = Dict[date, List[Tuple[str, float]]]


class Planner:
    def __init__(self, daily_availability: Dict[int, float]):
        """
        daily_availability keys map weekday index (0=Mon ... 6=Sun) to available hours.
        """
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

        # Higher urgency first: soonest due date, then higher priority number.
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
                    # Skip overdue tasks in this simple planner.
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
                    # Base-task fallback behavior.
                    chunk = task.recommended_daily_chunk(max(days_left, 1))
                    assigned = min(chunk, task.remaining_hours(), hours_left)
                    if assigned > 0:
                        schedule[current_day].append((task.name, assigned))
                        task.update_progress(assigned)
                        hours_left -= assigned

            current_day += timedelta(days=1)

        return schedule

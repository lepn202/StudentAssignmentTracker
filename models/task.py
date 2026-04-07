from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


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
        """Default strategy, intended to be overridden by subclasses."""
        if days_left <= 0:
            return self.remaining_hours()
        return self.remaining_hours() / days_left

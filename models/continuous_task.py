from __future__ import annotations

from dataclasses import dataclass

from models.task import Task


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

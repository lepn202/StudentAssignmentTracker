from __future__ import annotations

from dataclasses import dataclass

from models.task import Task


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

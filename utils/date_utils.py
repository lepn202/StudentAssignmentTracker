from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable


def date_range(start_date: date, end_date: date) -> Iterable[date]:
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)

# Student Assignment Tracker (Notebook-Friendly)

This project is a simple assignment planner designed to run cleanly in:

- Jupyter Notebook
- Google Colab
- Standard Python scripts

## Quick start (script mode)

```bash
python3 main.py
```

## Quick start (Jupyter/Colab)

```python
from datetime import date
import pandas as pd

from assignment_tracker import (
    Planner,
    ContinuousTask,
    NonContinuousTask,
    build_demo_tasks,
    schedule_rows,
)

today = date.today()
tasks = build_demo_tasks(today)

availability = {0: 2.0, 1: 2.0, 2: 2.0, 3: 2.0, 4: 2.0, 5: 3.0, 6: 3.0}
planner = Planner(availability)
end_date = max(t.due_date for t in tasks)
schedule = planner.build_schedule(tasks, today, end_date)

pd.DataFrame(schedule_rows(schedule))
```

## File layout

- `assignment_tracker.py`: all core classes and scheduling logic in one importable module for notebooks.
- `main.py`: simple script entrypoint.

## Notes

- Includes OOP with inheritance (`Task`, `ContinuousTask`, `NonContinuousTask`).
- Includes explicit `for`, `elif`, and `else` logic in scheduling behavior.

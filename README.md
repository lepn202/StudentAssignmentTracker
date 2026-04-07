# Student Assignment Tracker (Notebook + UI Friendly)

This project supports three ways to use the planner:

- **Web UI** with Streamlit (recommended for interactive input/editing)
- **Jupyter Notebook / Google Colab**
- **Standard Python script**

## 1) Run the UI (best for non-coders)

```bash
pip install -r requirements.txt
streamlit run app.py
```

In the UI you can:
- Add tasks with a form
- Edit/remove tasks in a table
- Set weekday study availability
- Generate a schedule

## 2) Run script mode

```bash
python3 main.py
```

## 3) Run in Jupyter/Colab

```python
from datetime import date, timedelta
import pandas as pd

from assignment_tracker import (
    Planner,
    ContinuousTask,
    NonContinuousTask,
    schedule_rows,
)

today = date.today()
tasks = [
    ContinuousTask(
        name="Essay",
        estimated_hours=6,
        due_date=today + timedelta(days=5),
        priority=5,
        course="English",
        created_at=today,
        min_session_hours=0.5,
        max_session_hours=2.0,
    ),
    NonContinuousTask(
        name="Worksheet",
        estimated_hours=2,
        due_date=today + timedelta(days=2),
        priority=4,
        course="Math",
        created_at=today,
    ),
]

availability = {0: 2.0, 1: 2.0, 2: 2.0, 3: 2.0, 4: 2.0, 5: 3.0, 6: 3.0}
planner = Planner(availability)
end_date = max(t.due_date for t in tasks)
schedule = planner.build_schedule(tasks, today, end_date)

pd.DataFrame(schedule_rows(schedule))
```

## File layout

- `assignment_tracker.py`: core classes and scheduling logic.
- `app.py`: Streamlit UI for task input/editing and schedule generation.
- `main.py`: script entrypoint.

## Notes

- Includes OOP with inheritance (`Task`, `ContinuousTask`, `NonContinuousTask`).
- Includes explicit `for`, `elif`, and `else` logic in scheduling behavior.
- Adds documented public/private class variables in code comments.

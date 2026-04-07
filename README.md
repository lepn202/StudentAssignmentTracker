# Student Assignment Tracker (Notebook + UI Friendly)

This project now supports three ways to use the planner:

- **Web UI** with Streamlit (recommended for interactive input/editing)
- **Jupyter Notebook / Google Colab**
- **Standard Python script**

## 1) Run the UI (best for non-coders)

```bash
pip install streamlit pandas
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

- `assignment_tracker.py`: all core classes and scheduling logic.
- `app.py`: Streamlit UI for input/editing and schedule generation.
- `main.py`: script entrypoint.

## Notes

- Includes OOP with inheritance (`Task`, `ContinuousTask`, `NonContinuousTask`).
- Includes explicit `for`, `elif`, and `else` logic in scheduling behavior.

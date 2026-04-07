# Student Assignment Tracker (Starter)

A simple Python starter app that demonstrates:

- Classes and inheritance (`Task`, `ContinuousTask`, `NonContinuousTask`)
- Scheduling assignments across a calendar
- Use of `for`, `elif`, and `else`

## Run

```bash
python3 main.py
```

## Files

- `models/task.py`: base class with shared assignment fields and behavior.
- `models/continuous_task.py`: tasks that can be split into chunks.
- `models/non_continuous_task.py`: tasks that should be done in one block.
- `scheduler/planner.py`: scheduling algorithm.
- `main.py`: demo input + printed schedule.

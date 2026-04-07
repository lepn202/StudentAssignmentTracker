## Run the UI 

```bash
pip install -r requirements.txt
streamlit run app.py
```

In the UI you can:
- Add tasks with a form
- Edit/remove tasks in a table
- Set weekday study availability
- Generate a schedule


## File layout

- `assignment_tracker.py`: core classes and scheduling logic.
- `app.py`: Streamlit UI for task input/editing and schedule generation.
- `main.py`: script entrypoint.

## Notes

- Includes OOP with inheritance (`Task`, `ContinuousTask`, `NonContinuousTask`).
- Includes explicit `for`, `elif`, and `else` logic in scheduling behavior.
- Adds documented public/private class variables in code comments.

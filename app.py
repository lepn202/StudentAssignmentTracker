"""
Streamlit UI for the Student Assignment Tracker.
Provides forms and data editors for users to manage tasks,
set their availability, and generate a study schedule.
"""

from __future__ import annotations

from datetime import date, datetime

import json
import os

import pandas as pd
import streamlit as st

from assignment_tracker import ContinuousTask, NonContinuousTask, Planner, Task

# Page configuration and title
st.set_page_config(page_title="Student Assignment Tracker", layout="wide")
st.title("Student Assignment Tracker")
st.caption("Add/edit assignments, then generate a study schedule.")

# Columns used for the task data
TASK_COLUMNS = [
    "name",
    "course",
    "task_type",
    "estimated_hours",
    "completed_hours",
    "status",
    "due_date",
    "priority",
    "min_session_hours",
    "max_session_hours",
]

DATA_FILE = "tracker_data.json"


def save_data():
    """Saves tasks, schedule, and availability to a JSON file."""
    data = {
        "tasks": [task.to_dict() for task in st.session_state.tasks],
        "schedule": [
            {"date": d.isoformat(), "task_name": t, "course": c, "scheduled_hours": h, "actual_hours": a}
            for d, sessions in st.session_state.schedule.items()
            for t, c, h, a in sessions
        ],
        "availability": st.session_state.availability,
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_data():
    """Loads tasks, schedule, and availability from a JSON file."""
    if not os.path.exists(DATA_FILE):
        return None
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data
    except Exception:
        return None


def to_rows(schedule):
    """
    Transforms the schedule dictionary into a list of rows for a DataFrame.

    Args:
        schedule (dict): A dictionary mapping dates to lists of (task_name, course, scheduled_hours, actual_hours) tuples.

    Returns:
        list: A list of dictionaries, each representing a row with 'date', 'task', 'course', 'scheduled_hours', and 'actual_hours'.
    """
    rows = []
    for day in sorted(schedule.keys()):
        for task_name, course, scheduled_hours, actual_hours in schedule[day]:
            rows.append({
                "date": day.isoformat(),
                "task": task_name,
                "course": course,
                "scheduled_hours": scheduled_hours,
                "actual_hours": actual_hours
            })
    return rows


# Initialize session state
if "initialized" not in st.session_state:
    loaded = load_data()
    if loaded:
        st.session_state.tasks = [Task.from_dict(t) for t in loaded["tasks"]]
        # availability keys in JSON are strings, convert back to int
        st.session_state.availability = {int(k): v for k, v in loaded["availability"].items()}

        # reconstruct schedule
        sched = {}
        for item in loaded["schedule"]:
            d = date.fromisoformat(item["date"])
            if d not in sched:
                sched[d] = []
            sched[d].append((item["task_name"], item["course"], item["scheduled_hours"], item["actual_hours"]))
        st.session_state.schedule = sched
    else:
        st.session_state.tasks = []
        st.session_state.availability = {i: 2.0 if i < 5 else 3.0 for i in range(7)}
        st.session_state.schedule = {}
    st.session_state.initialized = True


# Helper to sync DataFrame and Task objects
def tasks_to_df():
    if not st.session_state.tasks:
        return pd.DataFrame(columns=TASK_COLUMNS)
    return pd.DataFrame([t.to_dict() for t in st.session_state.tasks])


def update_tasks_from_df(df):
    new_tasks = []
    for row in df.to_dict(orient="records"):
        if not row.get("name"):
            continue
        new_tasks.append(Task.from_dict(row))
    st.session_state.tasks = new_tasks
    save_data()

# --- 1) Add a task ---
st.subheader("1) Add a task")
with st.form("add_task_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Task name")
        course = st.text_input("Course")
        task_type = st.selectbox("Task type", ["continuous", "non_continuous"])
    with c2:
        estimated_hours = st.number_input("Estimated hours", min_value=0.5, value=2.0, step=0.5)
        due_date_value = st.date_input("Due date", value=date.today())
        priority = st.slider("Priority", min_value=1, max_value=5, value=3)
    with c3:
        min_session_hours = st.number_input("Min session hours", min_value=0.25, value=0.5, step=0.25)
        max_session_hours = st.number_input("Max session hours", min_value=0.5, value=2.0, step=0.5)

    if st.form_submit_button("Add task") and name.strip():
        new_task_data = {
            "name": name.strip(),
            "course": course.strip() or "General",
            "task_type": task_type,
            "estimated_hours": float(estimated_hours),
            "due_date": due_date_value.isoformat(),
            "priority": int(priority),
            "min_session_hours": float(min_session_hours),
            "max_session_hours": float(max_session_hours),
            "created_at": date.today().isoformat(),
            "completed_hours": 0.0,
            "status": "not_started",
        }
        st.session_state.tasks.append(Task.from_dict(new_task_data))
        save_data()
        st.success(f"Added task: {new_task_data['name']}")
        st.rerun()

# --- 2) Edit tasks ---
st.subheader("2) Edit tasks")
tasks_df = tasks_to_df()
editable_df = st.data_editor(
    tasks_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "task_type": st.column_config.SelectboxColumn(
            "task_type", options=["continuous", "non_continuous"]
        ),
        "priority": st.column_config.NumberColumn("priority", min_value=1, max_value=5, step=1),
        "estimated_hours": st.column_config.NumberColumn("estimated_hours", min_value=0.5, step=0.5),
        "completed_hours": st.column_config.NumberColumn("completed_hours", min_value=0.0, step=0.5, disabled=True),
        "status": st.column_config.TextColumn("status", disabled=True),
        "min_session_hours": st.column_config.NumberColumn("min_session_hours", min_value=0.25, step=0.25),
        "max_session_hours": st.column_config.NumberColumn("max_session_hours", min_value=0.5, step=0.5),
        "created_at": None,  # Hide from user
    },
    key="tasks_editor"
)

if not tasks_df.equals(editable_df):
    update_tasks_from_df(editable_df)
    st.rerun()

# --- 3) Set weekly availability ---
st.subheader("3) Set weekly availability")
weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
availability_cols = st.columns(7)
new_availability = {}
for idx, day_name in enumerate(weekday_names):
    with availability_cols[idx]:
        val = st.number_input(
            day_name,
            min_value=0.0,
            value=float(st.session_state.availability.get(idx, 2.0)),
            step=0.5,
            key=f"avail_{idx}"
        )
        new_availability[idx] = val

if new_availability != st.session_state.availability:
    st.session_state.availability = new_availability
    save_data()

# --- 4) Study Schedule ---
st.subheader("4) Study Schedule")

def commit_schedule_progress():
    """Commits actual_hours from the schedule to the tasks."""
    if not st.session_state.schedule:
        return

    # Map tasks by (name, course) for quick lookup
    task_map = {(t.name, t.course): t for t in st.session_state.tasks}

    for day, sessions in st.session_state.schedule.items():
        for i, (name, course, scheduled, actual) in enumerate(sessions):
            if actual > 0:
                task = task_map.get((name, course))
                if task:
                    task.update_progress(actual)

    # Clear actual hours from schedule after committing to avoid double counting
    new_schedule = {}
    for day, sessions in st.session_state.schedule.items():
        new_schedule[day] = [(name, course, scheduled, 0.0) for name, course, scheduled, actual in sessions]
    st.session_state.schedule = new_schedule
    save_data()

if st.session_state.schedule:
    # Prepare data for display
    sched_rows = to_rows(st.session_state.schedule)
    sched_df = pd.DataFrame(sched_rows)

    # Format dates with weekdays
    today = date.today()
    def format_date(iso_str):
        d = date.fromisoformat(iso_str)
        fmt = d.strftime("%A, %b %d")
        if d == today:
            fmt += " (Today)"
        return fmt

    sched_df["display_date"] = sched_df["date"].apply(format_date)

    # Reorder and rename for UI
    display_df = sched_df[["display_date", "task", "course", "scheduled_hours", "actual_hours"]]

    st.write("Mark your progress by entering 'Actual Hours' spent on each session.")
    edited_sched_df = st.data_editor(
        display_df,
        use_container_width=True,
        column_config={
            "display_date": st.column_config.TextColumn("Date", disabled=True),
            "task": st.column_config.TextColumn("Task", disabled=True),
            "course": st.column_config.TextColumn("Course", disabled=True),
            "scheduled_hours": st.column_config.NumberColumn("Scheduled Hours", disabled=True),
            "actual_hours": st.column_config.NumberColumn("Actual Hours", min_value=0.0, step=0.5),
        },
        key="schedule_editor",
        hide_index=True
    )

    # Sync back to session_state.schedule if actual_hours changed
    if not display_df["actual_hours"].equals(edited_sched_df["actual_hours"]):
        new_schedule = {}
        for idx, row in edited_sched_df.iterrows():
            # Need to find the original date from sched_df using the index
            orig_row = sched_df.loc[idx]
            d = date.fromisoformat(orig_row["date"])
            if d not in new_schedule:
                new_schedule[d] = []
            new_schedule[d].append((row["task"], row["course"], row["scheduled_hours"], row["actual_hours"]))
        st.session_state.schedule = new_schedule
        save_data()
        st.rerun()

# --- Generate schedule logic ---
if st.session_state.schedule:
    st.info("A schedule already exists. Generating a new one will commit your current 'Actual Hours' and overwrite the plan.")
    confirm_gen = st.checkbox("I want to generate a new schedule starting from today.")
else:
    confirm_gen = True

if st.button("Generate Schedule", type="primary", disabled=not confirm_gen):
    commit_schedule_progress()
    tasks = st.session_state.tasks
    today = date.today()

    if not tasks:
        st.warning("Please add at least one valid task.")
    else:
        planner = Planner(st.session_state.availability)
        # Filter out completed tasks for scheduling
        active_tasks = [t for t in tasks if not t.is_completed()]
        if not active_tasks:
             st.success("All tasks are completed! No new schedule needed.")
             st.session_state.schedule = {}
             save_data()
        else:
            end_date = max(task.due_date for task in active_tasks)
            # build_schedule returns Dict[date, List[Tuple[str, str, float]]]
            raw_schedule = planner.build_schedule(active_tasks, start_date=today, end_date=end_date)

            # Convert to our session_state format: Date -> List of (task_name, course, scheduled, actual=0)
            new_schedule = {}
            for d, sessions in raw_schedule.items():
                new_schedule[d] = [(t, c, h, 0.0) for t, c, h in sessions]

            st.session_state.schedule = new_schedule
            save_data()
            st.success("New schedule generated!")
            st.rerun()

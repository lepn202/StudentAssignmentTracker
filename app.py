from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import streamlit as st

from assignment_tracker import ContinuousTask, NonContinuousTask, Planner, schedule_rows

st.set_page_config(page_title="Student Assignment Tracker", layout="wide")
st.title("Student Assignment Tracker")
st.caption("Add/edit assignments, then generate a study schedule.")

DEFAULT_COLUMNS = [
    "name",
    "course",
    "task_type",
    "estimated_hours",
    "due_date",
    "priority",
    "min_session_hours",
    "max_session_hours",
]

if "tasks_df" not in st.session_state:
    st.session_state.tasks_df = pd.DataFrame(
        [
            {
                "name": "History Essay",
                "course": "History",
                "task_type": "continuous",
                "estimated_hours": 8.0,
                "due_date": (date.today()).isoformat(),
                "priority": 5,
                "min_session_hours": 0.5,
                "max_session_hours": 2.0,
            }
        ]
    )

st.subheader("1) Add a task")
with st.form("add_task_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Task name", placeholder="Essay Draft")
        course = st.text_input("Course", placeholder="English")
        task_type = st.selectbox("Task type", ["continuous", "non_continuous"])
    with c2:
        estimated_hours = st.number_input("Estimated hours", min_value=0.5, value=2.0, step=0.5)
        due_date_value = st.date_input("Due date", value=date.today())
        priority = st.slider("Priority", min_value=1, max_value=5, value=3)
    with c3:
        min_session_hours = st.number_input("Min session hours", min_value=0.25, value=0.5, step=0.25)
        max_session_hours = st.number_input("Max session hours", min_value=0.5, value=2.0, step=0.5)

    submitted = st.form_submit_button("Add task")
    if submitted and name.strip():
        new_row = {
            "name": name.strip(),
            "course": course.strip() or "General",
            "task_type": task_type,
            "estimated_hours": float(estimated_hours),
            "due_date": due_date_value.isoformat(),
            "priority": int(priority),
            "min_session_hours": float(min_session_hours),
            "max_session_hours": float(max_session_hours),
        }
        st.session_state.tasks_df = pd.concat(
            [st.session_state.tasks_df, pd.DataFrame([new_row])],
            ignore_index=True,
        )
        st.success(f"Added task: {new_row['name']}")

st.subheader("2) Edit tasks")
st.write("You can edit any cell directly and remove rows.")
editable_df = st.data_editor(
    st.session_state.tasks_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "task_type": st.column_config.SelectboxColumn(
            "task_type", options=["continuous", "non_continuous"]
        ),
        "priority": st.column_config.NumberColumn("priority", min_value=1, max_value=5, step=1),
        "estimated_hours": st.column_config.NumberColumn("estimated_hours", min_value=0.5, step=0.5),
        "min_session_hours": st.column_config.NumberColumn("min_session_hours", min_value=0.25, step=0.25),
        "max_session_hours": st.column_config.NumberColumn("max_session_hours", min_value=0.5, step=0.5),
    },
)
st.session_state.tasks_df = editable_df[DEFAULT_COLUMNS].copy()

st.subheader("3) Set weekly availability")
weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
availability_cols = st.columns(7)
availability = {}
for idx, day_name in enumerate(weekday_names):
    with availability_cols[idx]:
        default_hours = 2.0 if idx < 5 else 3.0
        availability[idx] = st.number_input(day_name, min_value=0.0, value=default_hours, step=0.5)

if st.button("Generate schedule", type="primary"):
    rows = st.session_state.tasks_df.to_dict(orient="records")
    tasks = []
    today = date.today()

    for row in rows:
        if not row.get("name"):
            continue

        due_date_raw = row.get("due_date", today.isoformat())
        due_date_obj = datetime.fromisoformat(str(due_date_raw)).date()

        if row.get("task_type") == "non_continuous":
            task = NonContinuousTask(
                name=str(row["name"]),
                estimated_hours=float(row["estimated_hours"]),
                due_date=due_date_obj,
                priority=int(row["priority"]),
                course=str(row.get("course", "General")),
                created_at=today,
            )
        elif row.get("task_type") == "continuous":
            task = ContinuousTask(
                name=str(row["name"]),
                estimated_hours=float(row["estimated_hours"]),
                due_date=due_date_obj,
                priority=int(row["priority"]),
                course=str(row.get("course", "General")),
                created_at=today,
                min_session_hours=float(row.get("min_session_hours", 0.5)),
                max_session_hours=float(row.get("max_session_hours", 2.0)),
            )
        else:
            continue

        tasks.append(task)

    if not tasks:
        st.warning("Please add at least one valid task.")
    else:
        planner = Planner(availability)
        end_date = max(task.due_date for task in tasks)
        schedule = planner.build_schedule(tasks, start_date=today, end_date=end_date)

        schedule_df = pd.DataFrame(schedule_rows(schedule))
        if schedule_df.empty:
            st.warning("No schedule could be generated with the current inputs.")
        else:
            st.subheader("Generated schedule")
            st.dataframe(schedule_df, use_container_width=True)


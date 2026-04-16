
import unittest
from datetime import date, timedelta
from assignment_tracker import ContinuousTask, Planner

class TestAssignmentTrackerRounding(unittest.TestCase):
    def test_continuous_task_rounding(self):
        """Test that continuous tasks don't produce messy decimals in the schedule."""
        today = date.today()
        # 1.3 hours over 7 days (including today) will produce 0.1857...
        due_date = today + timedelta(days=6)

        task = ContinuousTask(
            name="Test Task",
            estimated_hours=1.3,
            due_date=due_date,
            priority=3,
            course="Testing",
            created_at=today,
            min_session_hours=0.1,
            max_session_hours=2.0
        )

        availability = {i: 6.0 for i in range(7)}
        planner = Planner(availability)

        schedule = planner.build_schedule([task], today, due_date)

        total_scheduled = 0.0
        for day, sessions in schedule.items():
            for task_name, course, hours in sessions:
                # Check decimal places
                self.assertLessEqual(len(str(hours).split('.')[-1]), 2, f"Hours {hours} on {day} has more than 2 decimal places")
                total_scheduled += hours

        # Total scheduled should be equal to estimated_hours (allowing for small float rounding if necessary,
        # but our rounding logic should make it exact)
        self.assertAlmostEqual(total_scheduled, 1.3, places=2)

    def test_planner_availability_rounding(self):
        """Test that hours_left in Planner also stays rounded."""
        today = date.today()
        due_date = today + timedelta(days=1)

        # Two tasks that together could cause precision issues
        task1 = ContinuousTask(
            name="Task 1",
            estimated_hours=0.333,
            due_date=due_date,
            priority=3,
            course="Testing",
            created_at=today
        )
        task2 = ContinuousTask(
            name="Task 2",
            estimated_hours=0.333,
            due_date=due_date,
            priority=2,
            course="Testing",
            created_at=today
        )

        availability = {i: 1.0 for i in range(7)}
        planner = Planner(availability)

        schedule = planner.build_schedule([task1, task2], today, due_date)

        for day, sessions in schedule.items():
            for _, _, hours in sessions:
                self.assertLessEqual(len(str(hours).split('.')[-1]), 2)

if __name__ == "__main__":
    unittest.main()

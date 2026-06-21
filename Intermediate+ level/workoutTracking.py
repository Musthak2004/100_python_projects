#!/usr/bin/env python3
"""
Workout Tracker - A comprehensive workout tracking application.

Features:
- Add workouts with exercises, sets, reps, weight, and duration
- View workout history
- Get workout statistics
- Data persistence using JSON
"""

import json
import os
from datetime import datetime
from typing import Optional
from collections import defaultdict


class WorkoutTracker:
    """A class to track workouts and provide statistics."""

    DATA_FILE = "workouts.json"

    def __init__(self):
        self.workouts = self._load_data()

    def _load_data(self) -> list:
        """Load workout data from JSON file."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_data(self):
        """Save workout data to JSON file."""
        with open(self.DATA_FILE, 'w') as f:
            json.dump(self.workouts, f, indent=2)

    def add_workout(self, workout_name: str, exercises: list, duration: int, date: Optional[str] = None):
        """
        Add a new workout session.

        Args:
            workout_name: Name of the workout (e.g., "Push Day", "Leg Day")
            exercises: List of exercise dictionaries with keys: name, sets, reps, weight
            duration: Duration in minutes
            date: Date string (YYYY-MM-DD), defaults to today
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        workout = {
            "id": len(self.workouts) + 1,
            "name": workout_name,
            "date": date,
            "duration": duration,
            "exercises": exercises
        }

        self.workouts.append(workout)
        self._save_data()
        print(f"Workout '{workout_name}' added successfully!")

    def view_workouts(self, limit: int = 10):
        """Display recent workouts."""
        if not self.workouts:
            print("No workouts recorded yet.")
            return

        print(f"\n{'='*60}")
        print("RECENT WORKOUTS")
        print(f"{'='*60}")

        for workout in self.workouts[-limit:]:
            print(f"\nDate: {workout['date']} | {workout['name']}")
            print(f"   Duration: {workout['duration']} minutes")
            print("   Exercises:")
            for ex in workout['exercises']:
                print(f"   - {ex['name']}: {ex['sets']} sets x {ex['reps']} reps @ {ex['weight']} lbs")

    def get_stats(self):
        """Display workout statistics."""
        if not self.workouts:
            print("No workouts to analyze.")
            return

        total_workouts = len(self.workouts)
        total_duration = sum(w['duration'] for w in self.workouts)
        total_exercises = sum(len(w['exercises']) for w in self.workouts)

        # Calculate most frequent exercises
        exercise_counts = defaultdict(int)
        exercise_volume = defaultdict(float)

        for workout in self.workouts:
            for ex in workout['exercises']:
                exercise_counts[ex['name']] += 1
                exercise_volume[ex['name']] += ex['sets'] * ex['reps'] * ex['weight']

        print(f"\n{'='*50}")
        print("WORKOUT STATISTICS")
        print(f"{'='*50}")
        print(f"Total Workouts: {total_workouts}")
        print(f"Total Duration: {total_duration} minutes")
        print(f"Total Exercises Logged: {total_exercises}")
        print(f"\nMost Frequent Exercises:")
        for ex, count in sorted(exercise_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"  • {ex}: {count} times")

        print(f"\nTop Volume Exercises:")
        for ex, vol in sorted(exercise_volume.items(), key=lambda x: -x[1])[:5]:
            print(f"  • {ex}: {vol:,.0f} total volume")

    def search_workouts(self, query: str):
        """Search workouts by name or date."""
        results = []
        for workout in self.workouts:
            if query.lower() in workout['name'].lower() or query in workout['date']:
                results.append(workout)

        if not results:
            print(f"No workouts found matching '{query}'")
            return

        print(f"\nFound {len(results)} workout(s) matching '{query}':")
        for w in results:
            print(f"  - {w['date']}: {w['name']}")


def create_exercise(name: str, sets: int, reps: int, weight: float) -> dict:
    """Create an exercise dictionary."""
    return {
        "name": name,
        "sets": sets,
        "reps": reps,
        "weight": weight
    }


def interactive_add_workout():
    """Interactive mode to add a workout."""
    tracker = WorkoutTracker()

    print("\nADD NEW WORKOUT")
    print("-" * 30)

    workout_name = input("Workout name: ").strip()
    if not workout_name:
        print("Workout name is required!")
        return

    duration = int(input("Duration (minutes): "))

    exercises = []
    while True:
        print(f"\n--- Exercise {len(exercises) + 1} ---")
        ex_name = input("Exercise name (or 'done' to finish): ").strip()
        if ex_name.lower() == 'done':
            break

        sets = int(input("Sets: "))
        reps = int(input("Reps: "))
        weight = float(input("Weight (lbs): "))

        exercises.append(create_exercise(ex_name, sets, reps, weight))

        cont = input("Add another exercise? (y/n): ").strip().lower()
        if cont != 'y':
            break

    tracker.add_workout(workout_name, exercises, duration)


def main():
    """Main CLI interface."""
    tracker = WorkoutTracker()

    while True:
        print(f"\n{'='*40}")
        print("   WORKOUT TRACKER")
        print(f"{'='*40}")
        print("1. Add Workout")
        print("2. View Recent Workouts")
        print("3. View Statistics")
        print("4. Search Workouts")
        print("5. Exit")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == '1':
            interactive_add_workout()
        elif choice == '2':
            tracker.view_workouts()
        elif choice == '3':
            tracker.get_stats()
        elif choice == '4':
            query = input("Search by name or date: ").strip()
            tracker.search_workouts(query)
        elif choice == '5':
            print("Goodbye! Keep crushing those workouts!")
            break
        else:
            print("Invalid option. Please select 1-5.")


if __name__ == "__main__":
    main()
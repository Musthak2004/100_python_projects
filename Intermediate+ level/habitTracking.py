import json
import os
import sys
import argparse
from datetime import date, timedelta

DATA_FILE = "habits.json"


def load_habits() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Failed to load habit data: {e}")
        return {}


def save_habits(habits: dict) -> bool:
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(habits, f, indent=2)
        return True
    except IOError as e:
        print(f"Failed to save habit data: {e}")
        return False


def add_habit(habits: dict, name: str) -> bool:
    if name in habits:
        print(f"Habit '{name}' already exists.")
        return False
    habits[name] = {
        "created": date.today().isoformat(),
        "history": [],
    }
    save_habits(habits)
    print(f"Habit '{name}' added.")
    return True


def delete_habit(habits: dict, name: str) -> bool:
    if name not in habits:
        print(f"Habit '{name}' not found.")
        return False
    del habits[name]
    save_habits(habits)
    print(f"Habit '{name}' deleted.")
    return True


def check_in(habits: dict, name: str, target: date | None = None) -> bool:
    if name not in habits:
        print(f"Habit '{name}' not found.")
        return False
    day = (target or date.today()).isoformat()
    if day in habits[name]["history"]:
        print(f"Habit '{name}' already checked for {day}.")
        return False
    habits[name]["history"].append(day)
    save_habits(habits)
    print(f"[x] {name} - checked for {day}")
    return True


def uncheck(habits: dict, name: str, target: date | None = None) -> bool:
    if name not in habits:
        print(f"Habit '{name}' not found.")
        return False
    day = (target or date.today()).isoformat()
    if day not in habits[name]["history"]:
        print(f"No check-in for {name} on {day}.")
        return False
    habits[name]["history"].remove(day)
    save_habits(habits)
    print(f"[ ] {name} - unchecked for {day}")
    return True


def current_streak(dates: list[str]) -> int:
    sorted_dates = sorted(set(dates), reverse=True)
    streak = 0
    today = date.today()
    for i, d in enumerate(sorted_dates):
        expected = (today - timedelta(days=i)).isoformat()
        if d == expected:
            streak += 1
        else:
            break
    return streak


def longest_streak(dates: list[str]) -> int:
    sorted_dates = sorted(set(dates))
    if not sorted_dates:
        return 0

    longest = 1
    current = 1
    for i in range(1, len(sorted_dates)):
        prev = date.fromisoformat(sorted_dates[i - 1])
        curr = date.fromisoformat(sorted_dates[i])
        if (curr - prev).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def show_status(habits: dict) -> None:
    if not habits:
        print("No habits yet. Use 'add <name>' to create one.")
        return

    today = date.today().isoformat()
    print(f"\n{'Habit':<20} {'Today':<8} {'Streak':<8} {'Created':<12}")
    print("-" * 48)
    for name, data in habits.items():
        checked = "[x]" if today in data["history"] else "[ ]"
        streak = current_streak(data["history"])
        created = data.get("created", "?")
        print(f"{name:<20} {checked:<8} {streak:<8} {created:<12}")


def show_stats(habits: dict, name: str) -> None:
    if name not in habits:
        print(f"Habit '{name}' not found.")
        return

    data = habits[name]
    history = sorted(set(data["history"]))
    total = len(history)
    cs = current_streak(history)
    ls = longest_streak(history)

    if history:
        first = date.fromisoformat(history[0])
        days_since_start = (date.today() - first).days + 1
        rate = total / days_since_start * 100
    else:
        days_since_start = 0
        rate = 0.0

    print(f"\nStats for '{name}'")
    print(f"  Created:       {data.get('created', '?')}")
    print(f"  Total check-ins: {total}")
    print(f"  Current streak:  {cs} day{'s' if cs != 1 else ''}")
    print(f"  Longest streak:  {ls} day{'s' if ls != 1 else ''}")
    print(f"  Completion rate: {rate:.1f}%")


def list_habits(habits: dict) -> None:
    if not habits:
        print("No habits yet.")
        return
    print(f"\nHabits ({len(habits)}):")
    for name in sorted(habits):
        total = len(habits[name]["history"])
        cs = current_streak(habits[name]["history"])
        print(f"  - {name} -- {total} check-ins, {cs}-day streak")


def main():
    parser = argparse.ArgumentParser(
        description="Habit Tracker - build and maintain daily routines."
    )
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Create a new habit")
    p_add.add_argument("name", help="Habit name")

    p_del = sub.add_parser("delete", help="Delete a habit")
    p_del.add_argument("name", help="Habit name")

    p_check = sub.add_parser("check", help="Check in for today")
    p_check.add_argument("name", help="Habit name")
    p_check.add_argument("--date", help="Date (YYYY-MM-DD) to check in for")

    p_uncheck = sub.add_parser("uncheck", help="Remove today's check-in")
    p_uncheck.add_argument("name", help="Habit name")
    p_uncheck.add_argument("--date", help="Date (YYYY-MM-DD) to uncheck")

    sub.add_parser("status", help="Show today's progress for all habits")
    sub.add_parser("list", help="List all habits")

    p_stats = sub.add_parser("stats", help="Show detailed stats for a habit")
    p_stats.add_argument("name", help="Habit name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    habits = load_habits()

    if args.command == "add":
        add_habit(habits, args.name)
    elif args.command == "delete":
        delete_habit(habits, args.name)
    elif args.command == "check":
        target = date.fromisoformat(args.date) if args.date else None
        check_in(habits, args.name, target)
    elif args.command == "uncheck":
        target = date.fromisoformat(args.date) if args.date else None
        uncheck(habits, args.name, target)
    elif args.command == "status":
        show_status(habits)
    elif args.command == "list":
        list_habits(habits)
    elif args.command == "stats":
        show_stats(habits, args.name)


if __name__ == "__main__":
    main()

import smtplib
import json
import datetime as dt
import random
import os
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"
BIRTHDAY_FILE = "birthdays.json"
LETTER_TEMPLATES = ["letter_1.txt", "letter_2.txt", "letter_3.txt"]


def load_birthdays(filepath: str) -> list[dict]:
    if not os.path.exists(filepath):
        print(f"Birthday file '{filepath}' not found.")
        return []

    with open(filepath, "r") as f:
        data = json.load(f)

    return data.get("birthdays", [])


def get_todays_birthdays(birthdays: list[dict]) -> list[dict]:
    today = dt.date.today()
    return [
        b for b in birthdays
        if b["month"] == today.month and b["day"] == today.day
    ]


def pick_random_letter() -> str:
    for template in LETTER_TEMPLATES:
        if os.path.exists(template):
            with open(template, "r") as f:
                content = f.read()
            if "[NAME]" in content:
                return content
            break
    return "Happy Birthday [NAME]! Wishing you a fantastic day!"


def send_email(recipient: str, name: str) -> bool:
    letter = pick_random_letter().replace("[NAME]", name)

    msg = MIMEText(letter)
    msg["Subject"] = f"Happy Birthday {name}!"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Birthday wish sent to {name} ({recipient})")
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP authentication failed. Check your email/password.")
    except smtplib.SMTPException as e:
        print(f"Failed to send email to {recipient}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False


def main():
    birthdays = load_birthdays(BIRTHDAY_FILE)
    if not birthdays:
        print("No birthdays loaded.")
        return

    todays = get_todays_birthdays(birthdays)
    if not todays:
        print("No birthdays today.")
        return

    print(f"Found {len(todays)} birthday(s) today!")
    for person in todays:
        send_email(person["email"], person["name"])


if __name__ == "__main__":
    main()

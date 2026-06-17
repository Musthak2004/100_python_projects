import smtplib
import time
import requests
from email.mime.text import MIMEText
from datetime import datetime, timezone

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"
RECIPIENT_EMAIL = "recipient_email@gmail.com"

MY_LAT = 51.5074
MY_LNG = -0.1278

ISS_API = "http://api.open-notify.org/iss-now.json"
SUNSET_API = "https://api.sunrise-sunset.org/json"
CHECK_INTERVAL = 60


def get_iss_position() -> tuple[float, float] | None:
    try:
        resp = requests.get(ISS_API, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        lat = float(data["iss_position"]["latitude"])
        lng = float(data["iss_position"]["longitude"])
        return lat, lng
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Failed to fetch ISS position: {e}")
        return None


def is_iss_overhead(lat: float, lng: float) -> bool:
    return abs(lat - MY_LAT) <= 5 and abs(lng - MY_LNG) <= 5


def get_sun_times() -> tuple[str, str] | None:
    params = {"lat": MY_LAT, "lng": MY_LNG, "formatted": 0}
    try:
        resp = requests.get(SUNSET_API, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        sunrise = data["results"]["sunrise"]
        sunset = data["results"]["sunset"]
        return sunrise, sunset
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Failed to fetch sun times: {e}")
        return None


def is_dark(sunrise: str, sunset: str) -> bool:
    now = datetime.now(timezone.utc)
    sunrise_dt = datetime.fromisoformat(sunrise)
    sunset_dt = datetime.fromisoformat(sunset)
    return now < sunrise_dt or now > sunset_dt


def send_notification() -> bool:
    subject = "ISS Overhead Notification"
    body = (
        f"Look up! The ISS is currently overhead at "
        f"({MY_LAT}, {MY_LNG}) and it is dark enough to see it."
    )
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("Notification sent.")
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP authentication failed. Check your email/password.")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False


def main():
    print("ISS Overhead Notifier started. Checking every 60 seconds...")
    while True:
        position = get_iss_position()
        if position:
            lat, lng = position
            print(f"ISS at ({lat:.2f}, {lng:.2f})", end="")

            if is_iss_overhead(lat, lng):
                print(" — overhead! Checking daylight...", end="")
                sun_times = get_sun_times()
                if sun_times:
                    sunrise, sunset = sun_times
                    if is_dark(sunrise, sunset):
                        print(" It's dark. Sending notification.")
                        send_notification()
                    else:
                        print(" Too bright. Skipping.")
                else:
                    print("")
            else:
                print("")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()

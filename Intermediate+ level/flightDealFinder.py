import smtplib
import json
import time
import requests
from email.mime.text import MIMEText
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


TEQUILA_API_KEY = "your_tequila_api_key"
TEQUILA_SEARCH_URL = "https://api.tequila.kiwi.com/v2/search"
TEQUila_LOCATIONS_URL = "https://api.tequila.kiwi.com/locations/query"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"

FROM_CITY = "LON"
CURRENCY = "GBP"
MAX_STOPOVERS = 0
MAX_FLIGHT_HOURS = 12
DAYS_AHEAD = 180
CHECK_INTERVAL = 86400

DATA_FILE = Path("flights_data.json")


def tequila_headers() -> dict:
    return {"apikey": TEQUILA_API_KEY}


@dataclass
class Destination:
    city: str
    iata: str
    target_price: float
    lowest_price: float = float("inf")
    last_alerted: Optional[str] = None


@dataclass
class FlightDeal:
    destination: Destination
    price: float
    airline: str
    departure: str
    arrival: str
    flight_no: str
    stops: int = 0
    duration: int = 0

    @property
    def savings(self) -> float:
        return round(self.destination.target_price - self.price, 2)

    @property
    def is_deal(self) -> bool:
        return self.price < self.destination.target_price


class DataManager:
    def __init__(self, filepath: Path = DATA_FILE):
        self.filepath = filepath
        self.destinations: list[Destination] = []
        self._load()

    def _load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, encoding="utf-8") as f:
                    data = json.load(f)
                self.destinations = [Destination(**d) for d in data]
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Failed to load data file: {e}")
                self._seed_defaults()
        else:
            self._seed_defaults()

    def _seed_defaults(self):
        self.destinations = [
            Destination("Paris", "PAR", 50),
            Destination("Berlin", "BER", 60),
            Destination("Tokyo", "TYO", 450),
            Destination("Sydney", "SYD", 550),
            Destination("Istanbul", "IST", 120),
            Destination("Kuala Lumpur", "KUL", 300),
            Destination("New York", "NYC", 300),
            Destination("San Francisco", "SFO", 350),
            Destination("Cape Town", "CPT", 400),
            Destination("Bali", "DPS", 350),
        ]
        self.save()

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([asdict(d) for d in self.destinations], f, indent=2)

    def get_iata_codes(self) -> list[str]:
        return [d.iata for d in self.destinations]

    def update_lowest(self, iata: str, price: float):
        for dest in self.destinations:
            if dest.iata == iata and price < dest.lowest_price:
                dest.lowest_price = price
                self.save()
                return True
        return False

    def should_alert(self, iata: str, price: float) -> bool:
        for dest in self.destinations:
            if dest.iata == iata and price < dest.target_price:
                if dest.last_alerted:
                    last = datetime.fromisoformat(dest.last_alerted)
                    if datetime.now() - last < timedelta(days=1):
                        return False
                return True
        return False

    def mark_alerted(self, iata: str):
        for dest in self.destinations:
            if dest.iata == iata:
                dest.last_alerted = datetime.now().isoformat()
                self.save()
                return


class FlightSearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(tequila_headers())

    def iata_code(self, city: str) -> Optional[str]:
        params = {"term": city, "location_types": "city", "limit": 1}
        try:
            resp = self.session.get(TEQUila_LOCATIONS_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data["locations"][0]["code"]
        except (requests.RequestException, KeyError, IndexError, ValueError) as e:
            print(f"Failed to get IATA for {city}: {e}")
            return None

    def search(self, fly_to: str) -> Optional[FlightDeal]:
        date_from = datetime.now().strftime("%d/%m/%Y")
        date_to = (datetime.now() + timedelta(days=DAYS_AHEAD)).strftime("%d/%m/%Y")

        params = {
            "fly_from": FROM_CITY,
            "fly_to": fly_to,
            "date_from": date_from,
            "date_to": date_to,
            "curr": CURRENCY,
            "max_stopovers": MAX_STOPOVERS,
            "flight_type": "oneway",
            "limit": 1,
            "sort": "price",
            "asc": 1,
        }

        try:
            resp = self.session.get(TEQUILA_SEARCH_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("data", [])
            if not results:
                return None

            flight = results[0]
            route = flight["route"][0]

            return FlightDeal(
                destination=Destination("", fly_to, 0),
                price=flight["price"],
                airline=route.get("airline", "Unknown"),
                departure=route["local_departure"],
                arrival=route["local_arrival"],
                flight_no=f"{route.get('airline', 'XX')}{route.get('flight_no', 0)}",
                stops=len(flight["route"]) - 1,
                duration=flight.get("duration", {}).get("total", 0) // 60,
            )
        except requests.RequestException as e:
            print(f"API error for {fly_to}: {e}")
        except (KeyError, IndexError, ValueError) as e:
            print(f"Parse error for {fly_to}: {e}")
        return None


class NotificationManager:
    @staticmethod
    def format_deal(deal: FlightDeal) -> str:
        lines = [
            f"Flight Deal Found!",
            f"{deal.destination.city} ({deal.destination.iata})",
            f"Price: {CURRENCY} {deal.price:.0f} (target: {CURRENCY} {deal.destination.target_price:.0f})",
            f"Savings: {CURRENCY} {deal.savings:.0f}",
            f"Airline: {deal.airline} ({deal.flight_no})",
            f"Depart: {deal.departure}",
            f"Arrive: {deal.arrival}",
        ]
        if deal.stops:
            lines.insert(4, f"Stops: {deal.stops}")
        return "\n".join(lines)

    @staticmethod
    def send_email(deals: list[FlightDeal]) -> bool:
        if not deals:
            return False

        body_parts = ["Flight Deal Summary\n"]
        for i, deal in enumerate(deals, 1):
            body_parts.append(f"--- Deal {i} ---")
            body_parts.append(NotificationManager.format_deal(deal))
            body_parts.append("")

        msg = MIMEText("\n".join(body_parts))
        msg["Subject"] = f"Flight Deals Found: {len(deals)} deal(s) below target!"
        msg["From"] = SENDER_EMAIL
        msg["To"] = SENDER_EMAIL

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            print(f"Deal email sent ({len(deals)} deals).")
            return True
        except smtplib.SMTPAuthenticationError:
            print("SMTP authentication failed.")
        except smtplib.SMTPException as e:
            print(f"Failed to send email: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        return False


class FlightDealFinder:
    def __init__(self):
        self.data = DataManager()
        self.searcher = FlightSearch()
        self.notifier = NotificationManager()

    def resolve_iata_codes(self):
        print("Resolving IATA codes...")
        for dest in self.data.destinations:
            code = self.searcher.iata_code(dest.city)
            if code:
                old = dest.iata
                dest.iata = code
                if old != code:
                    print(f"  {dest.city}: {old} -> {code}")
            else:
                print(f"  {dest.city}: keeping {dest.iata} (resolution failed)")

    def enrich_destinations(self):
        print("Enriching destination data from flights...")
        for dest in self.data.destinations:
            deal = self.searcher.search(dest.iata)
            if deal:
                deal.destination = dest
                print(f"  {dest.city}: best found {CURRENCY}{deal.price:.0f}")
                self.data.update_lowest(dest.iata, deal.price)
            else:
                print(f"  {dest.city}: no flights found")

    def check_deals(self) -> list[FlightDeal]:
        deals: list[FlightDeal] = []
        print(f"\nChecking deals from {FROM_CITY}...")
        for dest in self.data.destinations:
            print(f"  {dest.city} ({dest.iata}) target={CURRENCY}{dest.target_price:.0f}...", end=" ")
            deal = self.searcher.search(dest.iata)
            if deal:
                deal.destination = dest
                if deal.is_deal:
                    print(f"DEAL! {CURRENCY}{deal.price:.0f} (save {CURRENCY}{deal.savings:.0f})")
                    if self.data.should_alert(dest.iata, deal.price):
                        deals.append(deal)
                        self.data.mark_alerted(dest.iata)
                    else:
                        print("  (already alerted recently, skipping)")
                else:
                    print(f"{CURRENCY}{deal.price:.0f} (no deal)")
                self.data.update_lowest(dest.iata, deal.price)
            else:
                print("no results")
        return deals

    def run_once(self):
        print(f"\n{'='*50}")
        print(f"Flight Deal Finder — {datetime.now():%Y-%m-%d %H:%M}")
        print(f"{'='*50}")

        deals = self.check_deals()

        if deals:
            print(f"\n{len(deals)} deal(s) found! Sending notification...")
            self.notifier.send_email(deals)
        else:
            print("\nNo new deals to report.")

    def setup(self):
        print("Setting up Flight Deal Finder...")
        self.resolve_iata_codes()
        self.enrich_destinations()
        self.data.save()
        print(f"Setup complete. Tracking {len(self.data.destinations)} destinations.\n")

    def run_forever(self):
        print(f"Flight Deal Finder started. Checking every {CHECK_INTERVAL}s.")
        while True:
            self.run_once()
            print(f"\nNext check at {(datetime.now() + timedelta(seconds=CHECK_INTERVAL)):%H:%M}")
            time.sleep(CHECK_INTERVAL)


def main():
    import sys

    finder = FlightDealFinder()

    if "--setup" in sys.argv:
        finder.setup()
    elif "--once" in sys.argv:
        finder.run_once()
    elif "--check" in sys.argv:
        finder.check_deals()
    else:
        finder.run_forever()


if __name__ == "__main__":
    main()

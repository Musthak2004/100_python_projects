import json
import re
import smtplib
import requests
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional


TEQUILA_API_KEY = "your_tequila_api_key"
TEQUILA_SEARCH_URL = "https://api.tequila.kiwi.com/v2/search"
TEQUILA_LOCATIONS_URL = "https://api.tequila.kiwi.com/locations/query"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CLUB_EMAIL = "flightclub@example.com"
CLUB_PASSWORD = "your_app_password"

CURRENCY = "GBP"
MAX_STOPOVERS = 0
DAYS_AHEAD = 180

USERS_FILE = Path("flight_club_users.json")


def tequila_headers() -> dict:
    return {"apikey": TEQUILA_API_KEY}


@dataclass
class DestinationPref:
    city: str
    iata: str
    max_price: float
    lowest_found: float = float("inf")


@dataclass
class Member:
    name: str
    email: str
    home_iata: str
    joined: str = ""
    destinations: list[DestinationPref] = field(default_factory=list)
    notified: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.joined:
            self.joined = datetime.now().isoformat()

    def can_notify(self, iata: str) -> bool:
        if iata not in self.notified:
            return True
        last = datetime.fromisoformat(self.notified[iata])
        return datetime.now() - last > timedelta(hours=12)

    def mark_notified(self, iata: str):
        self.notified[iata] = datetime.now().isoformat()


EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
IATA_RE = re.compile(r"^[A-Z]{3}$")


class ClubData:
    def __init__(self, path: Path = USERS_FILE):
        self.path = path
        self.members: list[Member] = []
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, encoding="utf-8") as f:
                    raw = json.load(f)
                self.members = [Member(**m) for m in raw]
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Corrupt user data: {e}. Starting fresh.")
                self.members = []
        else:
            self.members = []

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([asdict(m) for m in self.members], f, indent=2, default=str)

    def find_member(self, email: str) -> Optional[Member]:
        return next((m for m in self.members if m.email == email), None)

    def register(self, name: str, email: str, home_iata: str) -> Optional[Member]:
        if not EMAIL_RE.match(email):
            print(f"Invalid email: {email}")
            return None
        if not IATA_RE.match(home_iata):
            print(f"Invalid IATA code: {home_iata} (must be 3 uppercase letters)")
            return None
        if self.find_member(email):
            print(f"Member with email {email} already exists.")
            return None
        member = Member(name=name, email=email, home_iata=home_iata)
        self.members.append(member)
        self.save()
        print(f"Welcome to the Flight Club, {name}!")
        return member

    def add_destination(self, email: str, city: str, iata: str, max_price: float) -> bool:
        member = self.find_member(email)
        if not member:
            print(f"No member found with email {email}.")
            return False
        if any(d.iata == iata for d in member.destinations):
            print(f"{city} ({iata}) is already in your list.")
            return False
        member.destinations.append(DestinationPref(city=city, iata=iata, max_price=max_price))
        self.save()
        print(f"Added {city} ({iata}) — max {CURRENCY}{max_price:.0f}")
        return True

    def remove_destination(self, email: str, iata: str) -> bool:
        member = self.find_member(email)
        if not member:
            return False
        before = len(member.destinations)
        member.destinations = [d for d in member.destinations if d.iata != iata]
        if len(member.destinations) < before:
            self.save()
            print(f"Removed {iata} from your list.")
            return True
        print(f"{iata} not found in your list.")
        return False

    def list_members(self):
        if not self.members:
            print("No members yet.")
            return
        print(f"\nFlight Club Members ({len(self.members)})")
        print("-" * 50)
        for m in self.members:
            dests = ", ".join(f"{d.city}({d.iata})" for d in m.destinations) or "none"
            print(f"  {m.name:20s} {m.email:30s} {m.home_iata}  [{dests}]")


class FlightSearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(tequila_headers())

    def search(self, fly_from: str, fly_to: str) -> Optional[dict]:
        date_from = datetime.now().strftime("%d/%m/%Y")
        date_to = (datetime.now() + timedelta(days=DAYS_AHEAD)).strftime("%d/%m/%Y")
        params = {
            "fly_from": fly_from,
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
            flights = data.get("data", [])
            if not flights:
                return None
            f = flights[0]
            route = f["route"][0]
            return {
                "price": f["price"],
                "airline": route.get("airline", "Unknown"),
                "flight_no": f"{route.get('airline', 'XX')}{route.get('flight_no', 0)}",
                "departure": route["local_departure"],
                "arrival": route["local_arrival"],
                "stops": len(f["route"]) - 1,
            }
        except requests.RequestException as e:
            print(f"  API error {fly_from}->{fly_to}: {e}")
        except (KeyError, IndexError, ValueError) as e:
            print(f"  Parse error {fly_from}->{fly_to}: {e}")
        return None

    def resolve_iata(self, city: str) -> Optional[str]:
        params = {"term": city, "location_types": "city", "limit": 1}
        try:
            resp = self.session.get(TEQUILA_LOCATIONS_URL, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()["locations"][0]["code"]
        except (requests.RequestException, KeyError, IndexError, ValueError):
            return None


class Notifier:
    @staticmethod
    def send_deal(member: Member, dest: DestinationPref, flight: dict) -> bool:
        savings = dest.max_price - flight["price"]
        body = (
            f"Hey {member.name},\n\n"
            f"Flight Deal from {member.home_iata} to {dest.city} ({dest.iata})!\n"
            f"{'='*40}\n"
            f"Price:      {CURRENCY}{flight['price']:.0f}\n"
            f"Target:     {CURRENCY}{dest.max_price:.0f}\n"
            f"Savings:    {CURRENCY}{savings:.0f}\n"
            f"Airline:    {flight['airline']} ({flight['flight_no']})\n"
            f"Departure:  {flight['departure']}\n"
            f"Arrival:    {flight['arrival']}\n"
            f"Stops:      {flight['stops']}\n\n"
            f"Book it before it's gone!\n"
            f"— Flight Club"
        )
        msg = MIMEText(body)
        msg["Subject"] = f"Flight Club Deal: {member.home_iata} → {dest.iata} for {CURRENCY}{flight['price']:.0f}"
        msg["From"] = CLUB_EMAIL
        msg["To"] = member.email
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(CLUB_EMAIL, CLUB_PASSWORD)
                server.send_message(msg)
            print(f"  Emailed {member.name} at {member.email}")
            return True
        except smtplib.SMTPAuthenticationError:
            print("  SMTP auth failed.")
        except smtplib.SMTPException as e:
            print(f"  Email error: {e}")
        except Exception as e:
            print(f"  Unexpected: {e}")
        return False


class FlightClub:
    def __init__(self):
        self.data = ClubData()
        self.searcher = FlightSearch()
        self.notifier = Notifier()

    def register_interactive(self):
        print("\n--- Flight Club Sign-Up ---")
        name = input("Your name: ").strip()
        email = input("Your email: ").strip()
        home = input("Home airport IATA (e.g. LON, NYC): ").strip().upper()
        self.data.register(name, email, home)

    def add_dest_interactive(self):
        email = input("Your email: ").strip()
        member = self.data.find_member(email)
        if not member:
            print("Member not found. Register first.")
            return
        city = input("Destination city: ").strip()
        iata = input("Airport IATA (or press Enter to auto-resolve): ").strip().upper()
        if not iata:
            resolved = self.searcher.resolve_iata(city)
            if not resolved:
                print(f"Could not resolve IATA for {city}. Try again manually.")
                return
            iata = resolved
            print(f"  Resolved {city} → {iata}")
        try:
            price = float(input(f"Max price ({CURRENCY}): "))
        except ValueError:
            print("Invalid price.")
            return
        self.data.add_destination(email, city, iata, price)

    def scan(self):
        print(f"\n{'='*50}")
        print(f"Flight Club Scan — {datetime.now():%Y-%m-%d %H:%M}")
        print(f"{'='*50}")
        found = 0
        for member in self.data.members:
            print(f"\n  {member.name} ({member.email}) from {member.home_iata}:")
            for dest in member.destinations:
                print(f"    {dest.city} ({dest.iata}) ≤ {CURRENCY}{dest.max_price:.0f}...", end=" ")
                flight = self.searcher.search(member.home_iata, dest.iata)
                if not flight:
                    print("no flights")
                    continue
                if flight["price"] < dest.max_price:
                    if flight["price"] < dest.lowest_found:
                        dest.lowest_found = flight["price"]
                    print(f"DEAL! {CURRENCY}{flight['price']:.0f}")
                    if member.can_notify(dest.iata):
                        self.notifier.send_deal(member, dest, flight)
                        member.mark_notified(dest.iata)
                        found += 1
                    else:
                        print("    (already notified, skipping)")
                else:
                    print(f"{CURRENCY}{flight['price']:.0f}")
            self.data.save()
        print(f"\nTotal deals sent: {found}")
        return found

    def show_member(self, email: str):
        member = self.data.find_member(email)
        if not member:
            print("Not found.")
            return
        print(f"\n{member.name} — {member.email} — {member.home_iata}")
        print(f"Joined: {member.joined[:10]}")
        if not member.destinations:
            print("No destinations tracked.")
            return
        print(f"{'City':20s} {'IATA':6s} {'Max':>8s} {'Best':>8s}")
        print("-" * 42)
        for d in member.destinations:
            best = f"{CURRENCY}{d.lowest_found:.0f}" if d.lowest_found < float("inf") else "---"
            print(f"{d.city:20s} {d.iata:6s} {CURRENCY}{d.max_price:>6.0f} {best:>8s}")


def main():
    import sys

    club = FlightClub()

    args = sys.argv[1:]
    if not args:
        print("Flight Club CLI")
        print("  register              — Sign up")
        print("  add                   — Add destination")
        print("  remove <email> <IATA> — Remove destination")
        print("  scan                  — Check all deals")
        print("  members               — List all members")
        print("  member <email>        — Show member details")
        return

    match args[0]:
        case "register":
            club.register_interactive()
        case "add":
            club.add_dest_interactive()
        case "remove":
            if len(args) >= 3:
                club.data.remove_destination(args[1], args[2].upper())
            else:
                print("Usage: remove <email> <IATA>")
        case "scan":
            club.scan()
        case "members":
            club.data.list_members()
        case "member":
            if len(args) >= 2:
                club.show_member(args[1])
            else:
                print("Usage: member <email>")
        case _:
            print(f"Unknown command: {args[0]}")


if __name__ == "__main__":
    main()

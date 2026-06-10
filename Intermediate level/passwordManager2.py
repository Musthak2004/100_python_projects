"""
Password Manager 2.0 (Intermediate)
====================================
An upgrade from the v1 plain-text JSON manager. Key additions:

  * Master-password protection with PBKDF2-HMAC-SHA256 key derivation
  * Fernet symmetric encryption for the vault file
  * Strong random password generator (using the `secrets` module)
  * Password strength meter (0-5 score)
  * Full CRUD: add, view, search, update, delete
  * Optional clipboard copy via `pyperclip` (auto-detected)

Dependencies (install once):
    pip install cryptography pyperclip
`pyperclip` is optional — the program works without it.
"""

import base64
import getpass
import json
import os
import secrets
import string
from datetime import datetime

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Optional clipboard support — silently degrades if not installed.
try:
    import pyperclip  # type: ignore
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


# --------------------------------------------------------------------------- #
#  Helper: strength evaluation
# --------------------------------------------------------------------------- #
class PasswordStrength:
    """Score a password from 0 (Very Weak) to 5 (Very Strong)."""

    LABELS = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]

    @classmethod
    def evaluate(cls, password: str) -> tuple[int, str]:
        if not password:
            return 0, cls.LABELS[0]

        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in string.punctuation for c in password):
            score += 1
        return min(score, 5), cls.LABELS[min(score, 5)]


# --------------------------------------------------------------------------- #
#  Helper: cryptographically-strong password generator
# --------------------------------------------------------------------------- #
class PasswordGenerator:
    """Generate passwords using the `secrets` module (CSPRNG)."""

    @staticmethod
    def generate(length: int = 16, use_upper: bool = True,
                 use_lower: bool = True, use_digits: bool = True,
                 use_symbols: bool = True) -> str:
        if length < 4:
            raise ValueError("Length must be at least 4.")

        pools: list[str] = []
        required: list[str] = []

        if use_lower:
            pools.append(string.ascii_lowercase)
            required.append(secrets.choice(string.ascii_lowercase))
        if use_upper:
            pools.append(string.ascii_uppercase)
            required.append(secrets.choice(string.ascii_uppercase))
        if use_digits:
            pools.append(string.digits)
            required.append(secrets.choice(string.digits))
        if use_symbols:
            pools.append(string.punctuation)
            required.append(secrets.choice(string.punctuation))

        if not pools:
            raise ValueError("At least one character set must be enabled.")

        alphabet = "".join(pools)
        # Fill the rest from the full alphabet, then Fisher–Yates shuffle
        # using `secrets` so position is also random.
        chars = required + [secrets.choice(alphabet) for _ in range(length - len(required))]
        for i in range(len(chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            chars[i], chars[j] = chars[j], chars[i]
        return "".join(chars)


# --------------------------------------------------------------------------- #
#  Crypto layer — derive an encryption key from a master password
# --------------------------------------------------------------------------- #
class CryptoManager:
    """Wrap PBKDF2 key derivation + Fernet encryption."""

    SALT_FILE = "vault.salt"
    KDF_ITERATIONS = 480_000  # OWASP 2023 baseline for PBKDF2-HMAC-SHA256

    def __init__(self, master_password: str) -> None:
        self.salt = self._load_or_create_salt()
        self.fernet = Fernet(self._derive_key(master_password, self.salt))

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=CryptoManager.KDF_ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _load_or_create_salt(self) -> bytes:
        if os.path.exists(self.SALT_FILE):
            with open(self.SALT_FILE, "rb") as f:
                return f.read()
        salt = os.urandom(16)
        with open(self.SALT_FILE, "wb") as f:
            f.write(salt)
        return salt

    def encrypt(self, plaintext: str) -> bytes:
        return self.fernet.encrypt(plaintext.encode())

    def decrypt(self, token: bytes) -> str:
        return self.fernet.decrypt(token).decode()


# --------------------------------------------------------------------------- #
#  Main vault — encrypted CRUD store
# --------------------------------------------------------------------------- #
class PasswordManager:
    """
    Encrypted password vault.

    Entries are stored in memory as:
        {
            "<service>": {
                "username":  str,
                "password":  str,
                "notes":     str,
                "created":   ISO-8601 timestamp,
                "updated":   ISO-8601 timestamp,
            },
            ...
        }
    and persisted as a single Fernet-encrypted JSON blob.
    """

    def __init__(self, filename: str = "vault.enc") -> None:
        self.filename = filename
        self.entries: dict[str, dict] = {}
        self.crypto = self._authenticate()

        if not self._load():
            # Brand-new vault — nothing to load.
            self.entries = {}

    # ---- authentication / file I/O ---------------------------------------
    def _authenticate(self) -> CryptoManager:
        """Prompt for the master password, creating a new vault if needed."""
        new_vault = not os.path.exists(self.filename)

        if new_vault:
            print("🔐 No vault found. Let's create one.")
            pw1 = getpass.getpass("   Set master password: ")
            pw2 = getpass.getpass("   Confirm master password: ")
            if pw1 != pw2:
                raise ValueError("Master passwords do not match.")
            if len(pw1) < 8:
                raise ValueError("Master password must be at least 8 characters.")
            print("✅ Vault created.\n")
            return CryptoManager(pw1)

        pw = getpass.getpass("🔐 Master password: ")
        try:
            return CryptoManager(pw)
        except Exception as exc:  # wrong password => Fernet raises InvalidToken
            raise ValueError("Could not unlock vault (wrong master password?)") from exc

    def _load(self) -> bool:
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            return False
        with open(self.filename, "rb") as f:
            token = f.read()
        self.entries = json.loads(self.crypto.decrypt(token))
        return True

    def _save(self) -> None:
        plaintext = json.dumps(self.entries, indent=2)
        with open(self.filename, "wb") as f:
            f.write(self.crypto.encrypt(plaintext))

    # ---- CRUD ------------------------------------------------------------
    def add(self, service: str, username: str, password: str, notes: str = "") -> None:
        now = datetime.now().isoformat(timespec="seconds")
        self.entries[service] = {
            "username": username,
            "password": password,
            "notes": notes,
            "created": now,
            "updated": now,
        }
        self._save()

    def get(self, service: str) -> dict | None:
        return self.entries.get(service)

    def search(self, query: str) -> dict[str, dict]:
        q = query.lower()
        return {s: d for s, d in self.entries.items() if q in s.lower()}

    def update(self, service: str, *, username=None, password=None, notes=None) -> bool:
        if service not in self.entries:
            return False
        entry = self.entries[service]
        if username is not None:
            entry["username"] = username
        if password is not None:
            entry["password"] = password
        if notes is not None:
            entry["notes"] = notes
        entry["updated"] = datetime.now().isoformat(timespec="seconds")
        self._save()
        return True

    def delete(self, service: str) -> bool:
        if service in self.entries:
            del self.entries[service]
            self._save()
            return True
        return False

    def services(self) -> list[str]:
        return sorted(self.entries.keys())


# --------------------------------------------------------------------------- #
#  UI helpers
# --------------------------------------------------------------------------- #
def hr(title: str) -> None:
    print("\n" + "=" * 56)
    print(f"  {title}")
    print("=" * 56)


def show_entry(service: str, data: dict, reveal: bool = False) -> None:
    print(f"\n📁 Service : {service}")
    print(f"👤 Username: {data.get('username', '')}")
    pw = data.get("password", "")
    print(f"🔑 Password: {pw if reveal else '*' * len(pw)}")
    if data.get("notes"):
        print(f"📝 Notes   : {data['notes']}")
    print(f"🕒 Created : {data.get('created', 'N/A')}")
    print(f"🕒 Updated : {data.get('updated', 'N/A')}")
    if reveal and CLIPBOARD_AVAILABLE:
        try:
            pyperclip.copy(pw)  # type: ignore
            print("📋 (Password copied to clipboard — clear it when done)")
        except Exception:
            pass


def prompt_strength(pw: str) -> None:
    score, label = PasswordStrength.evaluate(pw)
    bar = "█" * score + "░" * (5 - score)
    print(f"   Strength: [{bar}] {label} ({score}/5)")


# --------------------------------------------------------------------------- #
#  Menu flows
# --------------------------------------------------------------------------- #
def flow_add(manager: PasswordManager) -> None:
    hr("Add New Password")
    service = input("Service name: ").strip()
    if not service:
        print("❌ Service name cannot be empty.")
        return
    if service in manager.entries:
        print(f"⚠️  '{service}' already exists. Use Update to change it.")
        return

    username = input("Username / email: ").strip()

    if input("Generate a strong password? (y/N): ").strip().lower() == "y":
        password = flow_generate(interactive=True)
    else:
        password = getpass.getpass("Password: ")
        prompt_strength(password)

    notes = input("Notes (optional): ").strip()
    manager.add(service, username, password, notes)
    print(f"✅ Saved entry for '{service}'.")


def flow_view(manager: PasswordManager) -> None:
    hr("View Password")
    service = input("Service name: ").strip()
    data = manager.get(service)
    if not data:
        print(f"❌ No entry for '{service}'.")
        return
    show_entry(service, data, reveal=True)


def flow_search(manager: PasswordManager) -> None:
    hr("Search")
    query = input("Search query: ").strip()
    results = manager.search(query)
    if not results:
        print("No matches.")
        return
    print(f"\nFound {len(results)} match(es):")
    for s, d in results.items():
        print(f"  • {s}  ({d.get('username', '')})")


def flow_list(manager: PasswordManager) -> None:
    hr("All Services")
    services = manager.services()
    if not services:
        print("Vault is empty.")
        return
    for i, s in enumerate(services, 1):
        print(f"  {i:>3}. {s}")


def flow_update(manager: PasswordManager) -> None:
    hr("Update Password")
    service = input("Service name: ").strip()
    data = manager.get(service)
    if not data:
        print(f"❌ No entry for '{service}'.")
        return
    show_entry(service, data, reveal=True)

    print("\nPress Enter to keep the current value.")
    new_user = input(f"New username [{data['username']}]: ").strip() or data["username"]

    if input("Generate a new password? (y/N): ").strip().lower() == "y":
        new_pw = flow_generate(interactive=True)
    else:
        new_pw = getpass.getpass("New password (blank to keep): ") or data["password"]

    new_notes = input(f"New notes [{data.get('notes', '')}]: ").strip()
    if new_notes == "":
        new_notes = data.get("notes", "")

    manager.update(service, username=new_user, password=new_pw, notes=new_notes)
    print(f"✅ Updated '{service}'.")


def flow_delete(manager: PasswordManager) -> None:
    hr("Delete Password")
    service = input("Service name: ").strip()
    data = manager.get(service)
    if not data:
        print(f"❌ No entry for '{service}'.")
        return
    show_entry(service, data, reveal=True)
    confirm = input(f"\n⚠️  Type the service name exactly to confirm deletion: ").strip()
    if confirm == service:
        manager.delete(service)
        print(f"✅ Deleted '{service}'.")
    else:
        print("Cancelled.")


def flow_generate(interactive: bool = False) -> str:
    """Return a generated password; if interactive, ask for length first."""
    if interactive:
        try:
            length = int(input("Length (default 16, min 8): ").strip() or "16")
        except ValueError:
            length = 16
        length = max(length, 8)
    else:
        length = 16

    password = PasswordGenerator.generate(length)
    if interactive:
        print(f"\n✨ Generated: {password}")
        prompt_strength(password)
        if CLIPBOARD_AVAILABLE:
            try:
                pyperclip.copy(password)  # type: ignore
                print("📋 (Copied to clipboard)")
            except Exception:
                pass
    return password


def flow_strength() -> None:
    hr("Password Strength Checker")
    pw = getpass.getpass("Enter password to check: ")
    score, label = PasswordStrength.evaluate(pw)
    bar = "█" * score + "░" * (5 - score)
    print(f"\n   [{bar}] {label} ({score}/5)")
    print(f"   Length        : {len(pw)}")
    print(f"   Has lowercase  : {any(c.islower() for c in pw)}")
    print(f"   Has uppercase  : {any(c.isupper() for c in pw)}")
    print(f"   Has digits     : {any(c.isdigit() for c in pw)}")
    print(f"   Has symbols    : {any(c in string.punctuation for c in pw)}")


# --------------------------------------------------------------------------- #
#  Application entry point
# --------------------------------------------------------------------------- #
MENU = """
========================================================
              🔐  PASSWORD MANAGER 2.0
========================================================
  1. Add new password
  2. View password
  3. Search by service
  4. List all services
  5. Update password
  6. Delete password
  7. Generate strong password
  8. Check password strength
  9. Exit
--------------------------------------------------------"""


def main() -> None:
    print("🔐  Welcome to Password Manager 2.0")
    print("⚠️   There is NO recovery — remember your master password!")

    try:
        manager = PasswordManager()
    except ValueError as exc:
        print(f"❌ {exc}")
        return
    except Exception as exc:
        print(f"❌ Could not open vault: {exc}")
        return

    if not manager.entries:
        print("\nYour vault is empty. Add your first password to begin!")

    actions = {
        "1": flow_add,
        "2": flow_view,
        "3": flow_search,
        "4": flow_list,
        "5": flow_update,
        "6": flow_delete,
        "7": lambda _: flow_generate(interactive=True),
        "8": lambda _: flow_strength(),
    }

    while True:
        print(MENU)
        choice = input("Choose (1-9): ").strip()
        if choice == "9":
            print("👋 Goodbye! Stay secure.")
            break
        action = actions.get(choice)
        if not action:
            print("❌ Invalid choice.")
            continue
        try:
            action(manager)
        except KeyboardInterrupt:
            print("\nCancelled.")
        except Exception as exc:
            print(f"❌ Error: {exc}")


if __name__ == "__main__":
    main()

import json
import os

class PasswordManager:
    """
    A simple, file-based password manager for demonstration purposes.
    NOTE: For real security, use strong encryption (e.g., AES) and 
hashing.
    """
    def __init__(self, filename="passwords.json"):
        self.filename = filename
        self.passwords = {}  # Dictionary to hold {username: password}
        self._load_passwords()

    def _load_passwords(self):
        """Loads passwords from the JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.passwords = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Could not decode existing file. Starting with an empty list.")
                self.passwords = {}
        else:
            self.passwords = {}

    def _save_passwords(self):
        """Saves the current passwords dictionary back to the JSON 
file."""
        with open(self.filename, 'w') as f:
            json.dump(self.passwords, f, indent=4)

    def add_password(self):
        """Adds a new password entry."""
        print("\n--- Add New Password ---")
        username = input("Enter username/service name: ").strip()
        password = input("Enter password: ").strip()

        if not username or not password:
            print("Error: Both username and password are required.")
            return

        # Store the data
        self.passwords[username] = password
        self._save_passwords()
        print(f"\n✅ Successfully added password for '{username}'.")

    def view_passwords(self):
        """Displays all stored passwords."""
        if not self.passwords:
            print("\n\n📋 No passwords found. Start by adding one!")
            return

        print("\n=============================================")
        print("          PASSWORD MANAGER")
        print("=============================================")
        
        # Iterate through the dictionary and display (Note: passwords are displayed!)
        for user, pwd in self.passwords.items():
            print(f"Service: {user}")
            print(f"  Password: {pwd}\n")
        
        print("=============================================\n")

    def delete_password(self):
        """Deletes a password entry by username."""
        if not self.passwords:
            print("\n📋 Cannot delete. No passwords currently stored.")
            return

        username = input("Enter the username/service name to delete: ").strip()

        if username in self.passwords:
            del self.passwords[username]
            self._save_passwords()
            print(f"\n✅ Password for '{username}' has been successfully deleted.")
        else:
            print(f"\n❌ Error: Password for '{username}' not found.")

# --- Main Application Loop ---

def main():
    manager = PasswordManager()

    while True:
        print("\n=============================================")
        print("     PASSWORD MANAGER MENU")
        print("=============================================")
        print("1. Add Password")
        print("2. View All Passwords")
        print("3. Delete Password")
        print("4. Exit")
        print("---------------------------------------------")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            manager.add_password()
        elif choice == '2':
            manager.view_passwords()
        elif choice == '3':
            manager.delete_password()
        elif choice == '4':
            print("👋 Exiting Password Manager. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
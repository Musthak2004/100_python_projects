class CoffeeMachine:

    def __init__(self):

        self.resources = {
            "water": 1000,
            "milk": 500,
            "coffee": 300,
            "money": 0
        }

        self.menu = {
            "1": {
                "name": "Espresso",
                "water": 50,
                "milk": 0,
                "coffee": 18,
                "cost": 3
            },

            "2": {
                "name": "Latte",
                "water": 200,
                "milk": 150,
                "coffee": 24,
                "cost": 5
            },

            "3": {
                "name": "Cappuccino",
                "water": 250,
                "milk": 100,
                "coffee": 24,
                "cost": 4
            }
        }

        self.machine_on = True

    # Show menu
    def show_menu(self):

        print("\n===== MENU =====\n")

        for item in self.menu:

            coffee = self.menu[item]

            print(f"{item}. {coffee['name']}")
            print(f"Cost: ${coffee['cost']}")
            print()

    # User choice
    def get_user_choice(self):

        choice = None

        while choice not in ['1', '2', '3', 'report', 'off']:

            choice = input(
                "Select coffee (1/2/3)\n"
                "Type 'report' to see resources\n"
                "Type 'off' to stop machine\n"
                "Enter choice: "
            ).lower()

            if choice not in ['1', '2', '3', 'report', 'off']:
                print("Invalid choice!")

        return choice

    # Print report
    def print_report(self):

        print("\n===== MACHINE REPORT =====")
        print(f"Water : {self.resources['water']}ml")
        print(f"Milk  : {self.resources['milk']}ml")
        print(f"Coffee: {self.resources['coffee']}g")
        print(f"Money : ${self.resources['money']}")
        print("==========================")

    # Check resources
    def check_resources(self, coffee):

        if self.resources["water"] < coffee["water"]:
            print("Not enough water!")
            return False

        if self.resources["milk"] < coffee["milk"]:
            print("Not enough milk!")
            return False

        if self.resources["coffee"] < coffee["coffee"]:
            print("Not enough coffee!")
            return False

        return True

    # Process payment
    def process_payment(self, cost):

        print(f"\nCoffee cost: ${cost}")

        money = float(input("Enter money: $"))

        if money < cost:
            print("Not enough money!")
            return False

        change = money - cost

        if change > 0:
            print(f"Change returned: ${round(change, 2)}")

        self.resources["money"] += cost

        return True

    # Make coffee
    def make_coffee(self, coffee):

        self.resources["water"] -= coffee["water"]
        self.resources["milk"] -= coffee["milk"]
        self.resources["coffee"] -= coffee["coffee"]

        print(f"\nHere is your {coffee['name']}! Enjoy!")

    # Main machine loop
    def run(self):

        while self.machine_on:

            self.show_menu()

            choice = self.get_user_choice()

            if choice == "off":

                self.machine_on = False
                print("\nMachine turned OFF")

            elif choice == "report":

                self.print_report()

            else:

                selected_coffee = self.menu[choice]

                if self.check_resources(selected_coffee):

                    if self.process_payment(selected_coffee["cost"]):

                        self.make_coffee(selected_coffee)


# Create object
machine = CoffeeMachine()

# Start machine
machine.run()
print("===== COFFEE MACHINE =====\n")

resources = {
    "water": 1000,
    "milk": 500,
    "coffee": 300,
    "money": 0
}

menu = {
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
        "name": "Cappucino",
        "water": 250,
        "milk": 100,
        "coffee": 24,
        "cost": 4
    }
}

def showMenu():
    print("Menu Card:\n")
    for item in menu:
        coffee = menu[item]
        print(f"{item}. {coffee['name']}")
        print(f"Cost: ${coffee['cost']}")
        print()

def getUserChoice():
    choice = None
    while choice not in ["1", "2", "3", "off", "report"]:
        choice = input(
            "Select coffee (1/2/3)\n"
            "Type 'report' tp see resources\n"
            "Type 'off' to stop machine\n"
            "Enter choice: "
        ).lower()

        if choice not in ["1", "2", "3", "off", "report"]:
            print("Invalid choice!\n")

    return choice

def printReport():
    print("\n===== MACHINE REPORT =====")
    print(f"Water : {resources['water']}ml")
    print(f"Milk : {resources['milk']}ml")
    print(f"Coffee : {resources['coffee']}g")
    print(f"Money : ${resources['money']}")
    print("============================\n")

def checkResources(coffee):
    if resources['water'] < coffee["water"]:
        print("Not enough water!")
        return False
    
    if resources['milk'] < coffee['milk']:
        print("Not enough milk!")
        return False

    if resources["coffee"] < coffee["coffee"]:
        print("Not enough coffee!")
        return False
    
    return True

def processPayment(cost):
    print(f"\nCoffee cost: ${cost}")
    money = float(input("Enter money: $"))
    if money < cost:
        print("Not enough money!")
        return False
    
    change = money - cost

    if change > 0:
        print(f"Change returned: ${round(change, 2)}")

    resources['money'] += cost

    return True

def makeCoffee(coffee):
    resources['water'] -= coffee['water']
    resources['milk'] -= coffee['milk']
    resources['coffee'] -= coffee['coffee']

    print(f"\nHere is your {coffee['name']}! Enjoy!\n")

machine_on = True

while machine_on:
    showMenu()

    choice = getUserChoice()

    if choice == "off":
        machine_on = False
        print("\nCoffee Machine turned OFF")

    elif choice == "report":
        printReport()

    else:
        selectedCoffee = menu[choice]
        if checkResources(selectedCoffee):
            if processPayment(selectedCoffee['cost']):
                makeCoffee(selectedCoffee)

print("\n===== THANK YOU =====")
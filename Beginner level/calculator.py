def add(num1, num2):
    result = num1 + num2
    return result

def subtract(num1, num2):
    result = num1 - num2
    return result

def multiply(num1, num2):
    result = num1 * num2
    return result

def divide(num1, num2):
    if num2 == 0:
        return "Can't divide by ZERO"
    else:
        result = num1 / num2
        return result

while True:

    print("\n===== CALCULATOR =====")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "5":
        print("Calculator Closed!")
        break

    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    if choice == "1":
        print("Result: ", add(num1, num2))

    elif choice == "2":
        print("Result: ", subtract(num1, num2))

    elif choice == "3":
        print("Result: ", multiply(num1, num2))

    elif choice == "4":
        print("Result: ", divide(num1, num2))

    else:
        print("Invalid choice!")
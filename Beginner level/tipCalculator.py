print("***** Tip Calculator *****\n")

bill = float(input("What was the total bill? $"))
tipPercentage = int(input("What percentage tip would you like to give? (e.g, 10, 12, 15): "))
people = int(input("How many people to split the bill? "))

tipAmount = bill * (tipPercentage / 100)
totalBill = bill + tipAmount
billPerPerson = totalBill / people

print()
finalAmount = "{:.2f}".format(billPerPerson)
print(f"Each person should pay: ${finalAmount}")

print("\n**************************")
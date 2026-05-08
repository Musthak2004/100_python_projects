print("***** Welcome to Brand New Generator *****\n")

name = input("Enter your name: ")
word = input("Enter your favorite word: ")
number = input("Enter your lucky number: ")

print("\n- Your Generated Brand Names -\n")

brand1 = word + name + number
brand2 = name + "_" + word
brand3 = word.upper() + "X"
brand4 = name.title() + "Official"
brand5 = word.capitalize() + "_" + number

print("1.", brand1)
print("2.", brand2)
print("3.", brand3)
print("4.", brand4)
print("5.", brand5)

print("******************************************")

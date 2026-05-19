import random
import string

print("===== Password Generator =====")

while True:

    length = int(input("Enter password length (min 8): "))

    if length < 8:
        print("❌ Password too short! Try again.\n")
    else:
        break


letters = string.ascii_letters
numbers = string.digits
symbols = string.punctuation

all_characters = letters + numbers + symbols

password = ""

for i in range(length):
    password += random.choice(all_characters)

print("\n🔐 Generated Password:")
print(password)
import random

print("===== GUESS THE NUMBER =====")
print("I am thinking 1 to 100\n")

randomNumber = random.randint(1, 100)
attempt = 0

while True:

    user_input = input("Enter your guess: ")

    if user_input.isdecimal():

        user = int(user_input)
        attempt += 1

        if user > randomNumber:
            print("Too high!")

        elif user < randomNumber:
            print("Too low!")

        else:
            print("Correct! You won!")
            print(f"You guessed this number in {attempt} attempts")
            break

    else:
        print("Invalid input! Enter a number.")
import random

print("===== GUESS THE NUMBER (DEBUG VERSION) =====")
print("I am thinking of a number between 1 and 100\n")

randomNumber = random.randint(1, 100)
attempt = 0

while True:

    user_input = input("Enter your guess: ")

    print("DEBUG -> Raw input:", user_input)

    if user_input.isdecimal():

        user = int(user_input)

        print("DEBUG -> Converted number:", user)

        attempt += 1

        print("DEBUG -> Secret number:", randomNumber)

        if user > randomNumber:
            print("Too high!")

        elif user < randomNumber:
            print("Too low!")

        else:
            print("Correct! 🎉 You won!")
            print(f"You guessed it in {attempt} attempts")
            break

    else:
        print("Invalid input! Enter a number.")

    print("DEBUG -> Attempts so far:", attempt)
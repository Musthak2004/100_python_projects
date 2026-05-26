import random

print("===== SNAKE GAME + MAIL MERGE =====\n")

# Snake Game
snake_length = 3
score = 0

player_name = input("Enter your name: ")

while True:

    food = random.randint(1, 5)

    print(f"\nFood is at position: {food}")

    guess = int(input("Choose a position (1-5): "))

    if guess == food:

        snake_length += 1
        score += 1

        print("🍎 Food Eaten!")
        print("Snake Length:", snake_length)
        print("Score:", score)

    else:

        print("❌ Missed the food!")
        break

print("\n===== GAME OVER =====")
print("Final Score:", score)

# Mail Merge Part
letter_template = """
Hello [name],

Thank you for playing Snake Game!

Your Final Score : [score]
Your Snake Length : [length]

Keep practicing Python and build more awesome projects!

Regards,
Python Project Team
"""

personalized_letter = letter_template.replace(
    "[name]", player_name
)

personalized_letter = personalized_letter.replace(
    "[score]", str(score)
)

personalized_letter = personalized_letter.replace(
    "[length]", str(snake_length)
)

file_name = f"{player_name}_Result.txt"

with open(file_name, "w") as file:
    file.write(personalized_letter)

print(f"\n📧 Result letter saved as '{file_name}'")

print("\n===================================\n")

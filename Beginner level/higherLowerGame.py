import random

print("===== HIGHER LOWER GAME =====\n")

data = [
    {"name": "Cristiano Ronaldo", "followers": 600},
    {"name": "Taylor Swift", "followers": 300},
    {"name": "Instagram", "followers": 700},
    {"name": "YouTube", "followers": 500},
    {"name": "Elon Musk", "followers": 400}
]

a = random.choice(data)
b = random.choice(data)

print("A:", a["name"], "-", a["followers"], "M followers")
print("B:", b["name"], "-", b["followers"], "M followers")

user = input("\nWho has more followers? (a/b): ").lower()

if a["followers"] > b["followers"]:
    correct = "a"
else:
    correct = "b"

if user == correct:
    print("Correct!")
else:
    print("You Lose!")

print("\n*****************************")
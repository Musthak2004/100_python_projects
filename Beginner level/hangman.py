word = "apple"

display = []

for letter in word:
    display.append("_")

lives = 6

while lives > 0:
    print("\nCurrent Word:", " ".join(display))
    print("Lives Left:", lives)

    guess = input("Guess a letter: ").lower()

    if guess in word:
        for position in range(len(word)):
            if word[position] == guess:
                display[position] = guess

        print("Correct Guess!")
    
    else:
        lives -= 1
        print("Wrong Guess!")

    if "_" not in display:
        print("\nYOU WON!")
        print("The word was:", word)
        break

if "_" in display:
    print("\nGAME OVER!")
    print("The word was:", word)
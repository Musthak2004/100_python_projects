print("Welcome to Treasure Island!")
print("Your mission is to find the treasure.\n")

choice1 = input("You're at a crossroad. Where do you want to go? (left/right): ")

if choice1 == "left":

    choice2 = input("You came to a lake. Swim or wait? (swim/wait): ").lower()

    if choice2 == 'wait':

        choice3 = input("You arrive at 3 doors: red, blue, yellow. Which one? ").lower()

        if choice3 == "yellow":
            print("You found the treasure! You Win!")

        elif choice3 == "red":
            print("Burned by fire. Game Over!")
        
        elif choice3 == "blue":
            print("Eaten by beasts. Game Over!")

        else:
            print("Invalid door. Game Over!")

    else:
        print("You got attacked by a crocodile. Game Over!")

else:
    print("You fell into a hole. Game Over!")

print("\nGame Finished.")
import random

print("===== Rock Paper Scissors Game =====")

def getUserChoice():
    player = None

    while player not in ['r', 'p', 's']:

        print("\nChoose one:")
        print("r = Rock")
        print("p = Paper")
        print("s = Scissors")

        player = input("Enter your choice: ").lower()

        if player not in ['r', 'p', 's']:
            print("Invalid choice! Try again.\n")

    return player


def getComputerChoice():
    num = random.randint(1, 3)

    if num == 1:
        return 'r'
    elif num == 2:
        return 'p'
    else:
        return 's'


def showChoice(choice):
    if choice == 'r':
        print("Rock\n")
    elif choice == 'p':
        print("Paper\n")
    else:
        print("Scissors\n")


def chooseWinner(player, computer):

    if player == computer:
        print("It's a tie\n")

    elif player == 'r':
        if computer == 's':
            print("YOU WIN!\n")
        else:
            print("YOU LOSE!\n")

    elif player == 'p':
        if computer == 'r':
            print("YOU WIN!\n")
        else:
            print("YOU LOSE!\n")

    elif player == 's':
        if computer == 'p':
            print("YOU WIN!\n")
        else:
            print("YOU LOSE!\n")


playAgain = 'y'

while playAgain.lower() == 'y':

    player = getUserChoice()

    print("\nYour choice:")
    showChoice(player)

    computer = getComputerChoice()

    print("Computer choice:")
    showChoice(computer)

    chooseWinner(player, computer)

    playAgain = input("Play again? (y/n): ")

    print("\n")

print("Thanks for playing!")
print("====================================")
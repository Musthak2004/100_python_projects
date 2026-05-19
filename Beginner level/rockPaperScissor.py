import random

print("===== Rock Paper Scissors Game =====")

def getUserInput():
    player = None

    while player not in ['r', 'p', 's']:

        print("\nChoose one:")
        print("r = Rock")
        print("p = Paper")
        print("s = Scissors")

        player = input("Enter your choice: ").lower()

        if player not in ['r', 'p', 's']:
            print("❌ Invalid choice! Try again.\n")

    return player

def getComputerChoice():
    num = random.randint(1, 3)
    
    match num:
        case 1:
            return 'r'
        case 2:
            return 'p'
        case 3:
            return 's'
        
    return 'r'

def showChoice(choice):
    match choice:
        case 'r':
            print("Rock\n")
        case 'p':
            print("Rock\n")
        case 's':
            print("Scissors\n")

def chooseWinner(player, computer):
    if player == computer:
        print("It's a tie\n")

print("====================================")
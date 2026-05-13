import random

print("===== BLACKJACK GAME =====\n")

name = input("What is your name? ")

card1 = random.randint(1,10)
card2 = random.randint(1,10)

total = card1 + card2

print("\nYour cards:")
print("Card 1 =", card1)
print("Card 2 =", card2)
print("Total =", total)

dealer = random.randint(15, 21)

print("\nDealer Score =", dealer)

if total > 21:
    print("\n Bust! You Lose")
elif total > dealer:
    print("\n You Win!")
elif total == dealer:
    print("\n Draw!")
else:
    print("\n Dealer Wins")

print("===== GAME OVER =====\n")

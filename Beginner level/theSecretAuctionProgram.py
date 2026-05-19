print("===== SECRET AUCTION PROGRAM =====")

bidders = {}

bidding_finished = False

def find_highest_bid(bidding_record):
    highest_bid = 0
    winner = ""

    for name in bidding_record:
        bid_amount = bidding_record[name]

        if bid_amount > highest_bid:
            highest_bid = bid_amount
            winner = name

    print(f"\nWinner is {winner} with bid of {highest_bid}")

while not bidding_finished:

    name = input("Enter bidder name: ")
    bid = int(input("Enter your bid amount: "))

    bidders[name] = bid

    more = input("Are there more bidders? (yes/no): ").lower()

    if more == "no":
        bidding_finished = True
        find_highest_bid(bidders)
    else:
        print("\n" * 20)
def show_position(x, y):
    print(f"\nPlayer Position: ({x}, {y})")


# Starting position
x = 0
y = 0

# Exit position
exit_x = 2
exit_y = 2

print("===== ESCAPE THE MAZE =====")
print("Reach position (2, 2) to escape!")
print("Commands: up, down, left, right")

while True:

    show_position(x, y)

    move = input("\nEnter move: ").lower()

    # Move Up
    if move == "up":
        y -= 1

    # Move Down
    elif move == "down":
        y += 1

    # Move Left
    elif move == "left":
        x -= 1

    # Move Right
    elif move == "right":
        x += 1

    else:
        print("Invalid command!")
        continue

    # Wall boundary
    if x < 0 or y < 0 or x > 2 or y > 2:
        print("❌ You hit a wall!")
        
        # Move back
        if move == "up":
            y += 1

        elif move == "down":
            y -= 1

        elif move == "left":
            x += 1

        elif move == "right":
            x -= 1

    # Escape check
    if x == exit_x and y == exit_y:
        print("\n🎉 YOU ESCAPED THE MAZE!")
        break
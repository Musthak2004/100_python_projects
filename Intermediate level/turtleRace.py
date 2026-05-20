import turtle
import random

screen = turtle.Screen()
screen.title("Turtle Race Game")
screen.setup(width=700, height=500)

user_bet = screen.textinput(
    title="Make your bet",
    prompt="Which turtle will win? (red/blue/green/yellow/orange/purple): "
)

colors = ["red", "blue", "green", "yellow", "orange", "purple"]

all_turtles = []

start_y = -100

for color in colors:
    new_turtle = turtle.Turtle()
    new_turtle.shape("turtle")
    new_turtle.color(color)
    new_turtle.penup()
    new_turtle.goto(x=-320, y=start_y)

    all_turtles.append(new_turtle)
    start_y += 40

race_on = True

while race_on:
    for t in all_turtles:
        move_distance = random.randint(1, 10)
        t.forward(move_distance)

        if t.xcor() > 320:
            race_on = False
            winning_color = t.pencolor()

            if winning_color == user_bet:
                print(f"You win! {winning_color} turtle is the winner!")
            else:
                print(f"You lost! {winning_color} turtle won!")
            break

screen.exitonclick()
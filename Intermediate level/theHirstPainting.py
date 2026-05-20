import turtle
import random

screen = turtle.Screen()
screen.title("Hirst Painting")

artist = turtle.Turtle()

artist.speed("fastest")

artist.hideturtle()

artist.penup()

turtle.colormode(255)

colors = [
    (239, 83, 80),
    (66, 165, 245),
    (255, 238, 88),
    (102, 187, 106),
    (171, 71, 188),
    (255, 167, 38),
    (38, 198, 218),
    (141, 110, 99),
    (255, 112, 67),
    (124, 179, 66)
]

artist.goto(-250, -250)

number_of_dots = 100

for dot_count in range(1, number_of_dots + 1):
    random_color = random.choice(colors)
    artist.dot(20, random_color)
    artist.forward(50)

    if dot_count % 10 == 0:
        y =artist.ycor()  + 50
        artist.goto(-250, y)

screen.exitonclick()
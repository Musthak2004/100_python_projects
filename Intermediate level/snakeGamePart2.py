import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor

class SnakeGame(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Snake Game - Part 2")
        self.setGeometry(300, 300, 600, 400)

        self.snake = [[100, 100], [90, 100], [80, 100]]

        self.direction = "RIGHT"

        self.food = self.generate_food()

        self.score = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(150)

        self.show()

    def game_loop(self):
        self.move_snake()
        self.check_collision()
        self.update()

    def move_snake(self):
        head_x, head_y = self.snake[0]

        if self.direction == "RIGHT":
            head_x += 10
        elif self.direction == "LEFT":
            head_x -= 10
        elif self.direction == "UP":
            head_x -= 10
        elif self.direction == "DOWN":
            head_x += 10

        new_head = [head_x, head_y]

        self.snake.insert(0, new_head)

        if new_head != self.food:
            self.snake.pop()
        else:
            self.score += 1
            self.food = self.generate_food()

    def generate_food(self):
        x = random.randint(0, 59) * 10
        y = random.randint(0, 39) * 10

        return [x, y]

app = QApplication(sys.argv)
game = SnakeGame()
sys.exit(app.exec_())
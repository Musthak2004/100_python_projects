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

        # Snake body
        self.snake = [[100, 100], [90, 100], [80, 100]]

        self.direction = "RIGHT"

        # Food position
        self.food = self.generate_food()

        # Score
        self.score = 0

        # Game loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(150)

        self.show()

    # Game loop
    def game_loop(self):
        self.move_snake()
        self.check_collision()
        self.update()

    # Move snake
    def move_snake(self):

        head_x, head_y = self.snake[0]

        if self.direction == "RIGHT":
            head_x += 10
        elif self.direction == "LEFT":
            head_x -= 10
        elif self.direction == "UP":
            head_y -= 10
        elif self.direction == "DOWN":
            head_y += 10

        new_head = [head_x, head_y]

        self.snake.insert(0, new_head)

        # If NOT eating food → remove tail
        if new_head != self.food:
            self.snake.pop()
        else:
            self.score += 1
            self.food = self.generate_food()

    # Generate food
    def generate_food(self):

        x = random.randint(0, 59) * 10
        y = random.randint(0, 39) * 10

        return [x, y]

    # Collision check
    def check_collision(self):

        head = self.snake[0]

        # wall collision
        if head[0] < 0 or head[0] > 590 or head[1] < 0 or head[1] > 390:
            self.game_over()

        # self collision
        if head in self.snake[1:]:
            self.game_over()

    # Game over
    def game_over(self):
        print(f"Game Over! Score: {self.score}")
        self.timer.stop()

    # Keyboard
    def keyPressEvent(self, event):

        key = event.key()

        if key == Qt.Key_Right and self.direction != "LEFT":
            self.direction = "RIGHT"
        elif key == Qt.Key_Left and self.direction != "RIGHT":
            self.direction = "LEFT"
        elif key == Qt.Key_Up and self.direction != "DOWN":
            self.direction = "UP"
        elif key == Qt.Key_Down and self.direction != "UP":
            self.direction = "DOWN"

    # Draw everything
    def paintEvent(self, event):

        painter = QPainter(self)

        # Draw snake
        painter.setBrush(QColor(0, 255, 0))

        for block in self.snake:
            painter.drawRect(block[0], block[1], 10, 10)

        # Draw food
        painter.setBrush(QColor(255, 0, 0))
        painter.drawRect(self.food[0], self.food[1], 10, 10)


# Run game
app = QApplication(sys.argv)
game = SnakeGame()
sys.exit(app.exec_())
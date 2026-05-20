import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, Qt


class SnakeGame(QWidget):

    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("Snake Game - Part 1")
        self.setGeometry(300, 300, 600, 400)

        # Snake initial position (3 blocks)
        self.snake = [
            [100, 100],
            [90, 100],
            [80, 100]
        ]

        # Direction (moving right)
        self.direction = "RIGHT"

        # Timer (game loop)
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(150)  # speed

        self.show()

    # Game loop (runs again and again)
    def game_loop(self):

        self.move_snake()
        self.update()  # refresh screen

    # Move snake logic
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

        # new head
        new_head = [head_x, head_y]

        # move snake body
        self.snake.insert(0, new_head)
        self.snake.pop()

    # Keyboard control
    def keyPressEvent(self, event):

        key = event.key()

        if key == Qt.Key_Right:
            self.direction = "RIGHT"
        elif key == Qt.Key_Left:
            self.direction = "LEFT"
        elif key == Qt.Key_Up:
            self.direction = "UP"
        elif key == Qt.Key_Down:
            self.direction = "DOWN"


# Run app
app = QApplication(sys.argv)
game = SnakeGame()
sys.exit(app.exec_())
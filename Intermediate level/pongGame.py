import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter

class PongGame(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pong Game")
        self.setGeometry(100, 100, 800, 600)

        self.left_paddle_y = 250
        self.right_paddle_y = 250

        self.paddle_width = 15
        self.paddle_height = 100

        self.ball_x = 390
        self.ball_y = 290

        self.ball_size = 20

        self.ball_dx = 5
        self.ball_dy = 5

        self.left_score = 0
        self.right_score = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(16)

    def game_loop(self):

        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        if self.ball_y <= 0:
            self.ball_dy *= -1

app = QApplication(sys.argv)
game = PongGame()
game.show()

sys.exit(app.exec_())
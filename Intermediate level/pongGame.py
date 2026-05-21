import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter


class PongGame(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pong Game")
        self.setGeometry(100, 100, 800, 600)

        # Paddles
        self.left_paddle_y = 250
        self.right_paddle_y = 250

        self.paddle_width = 15
        self.paddle_height = 100

        # Ball
        self.ball_x = 390
        self.ball_y = 290

        self.ball_size = 20

        self.ball_dx = 5
        self.ball_dy = 5

        # Scores
        self.left_score = 0
        self.right_score = 0

        # Game loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(16)  # ~60 FPS

    def game_loop(self):

        # Move ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Top/Bottom wall collision
        if self.ball_y <= 0:
            self.ball_dy *= -1

        if self.ball_y >= self.height() - self.ball_size:
            self.ball_dy *= -1

        # Paddle rectangles
        left_rect = QRect(
            20,
            self.left_paddle_y,
            self.paddle_width,
            self.paddle_height
        )

        right_rect = QRect(
            self.width() - 35,
            self.right_paddle_y,
            self.paddle_width,
            self.paddle_height
        )

        ball_rect = QRect(
            self.ball_x,
            self.ball_y,
            self.ball_size,
            self.ball_size
        )

        # Paddle collision
        if ball_rect.intersects(left_rect):
            self.ball_dx = abs(self.ball_dx)

        if ball_rect.intersects(right_rect):
            self.ball_dx = -abs(self.ball_dx)

        # Score check
        if self.ball_x < 0:
            self.right_score += 1
            self.reset_ball()

        if self.ball_x > self.width():
            self.left_score += 1
            self.reset_ball()

        self.update()

    def reset_ball(self):

        self.ball_x = self.width() // 2
        self.ball_y = self.height() // 2

        self.ball_dx *= -1

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_W:
            self.left_paddle_y -= 20

        elif event.key() == Qt.Key_S:
            self.left_paddle_y += 20

        elif event.key() == Qt.Key_Up:
            self.right_paddle_y -= 20

        elif event.key() == Qt.Key_Down:
            self.right_paddle_y += 20

        # Keep paddles inside window
        self.left_paddle_y = max(
            0,
            min(self.left_paddle_y,
                self.height() - self.paddle_height)
        )

        self.right_paddle_y = max(
            0,
            min(self.right_paddle_y,
                self.height() - self.paddle_height)
        )

    def paintEvent(self, event):

        painter = QPainter(self)

        # Left paddle
        painter.drawRect(
            20,
            self.left_paddle_y,
            self.paddle_width,
            self.paddle_height
        )

        # Right paddle
        painter.drawRect(
            self.width() - 35,
            self.right_paddle_y,
            self.paddle_width,
            self.paddle_height
        )

        # Ball
        painter.drawEllipse(
            self.ball_x,
            self.ball_y,
            self.ball_size,
            self.ball_size
        )

        # Score
        painter.drawText(
            330,
            40,
            f"{self.left_score} : {self.right_score}"
        )


app = QApplication(sys.argv)

game = PongGame()
game.show()

sys.exit(app.exec_())
import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter

class TurtleCrossing(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Turtle Crossing")
        self.setGeometry(100, 100, 800, 600)

        #Player
        self.player_x = 390
        self.player_y = 550
        self.player_size = 20

        #Cars
        self.cars = []

        #Level
        self.level = 1
        self.car_speed = 5

        self.create_cars()

        #Game Loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(30)

    def create_cars(self):
        for _ in range(10):
            car = {
                "x": random.randint(0, 800),
                "y": random.randint(50, 500),
                "width": 50,
                "height": 20
            }

            self.cars.append(car)

    def game_loop(self):
        #Move Cars
        for car in self.cars:
            car["x"] += self.car_speed

            if car["x"] > self.width():
                car["x"] = -car["width"]

        #Collision Check
        player_rect = QRect(
            self.player_x,
            self.player_y,
            self.player_size,
            self.player_size
        )

        for car in self.cars:
            car_rect = QRect(
                car["x"],
                car["y"],
                car["width"],
                car["height"]
            )

            if player_rect.intersects(car_rect):
                print("Game Over!")
                self.timer.stop()

        #Level Complete
        if self.player_y <= 0:
            self.level += 1
            self.car_speed += 1

            self.player_x = 390
            self.player_y = 550

            print(f"Level {self.level}")

        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.player_y -= 20

        elif event.key() == Qt.Key_Down:
            self.player_y += 20

        elif event.key() == Qt.Key_Left:
            self.player_x -= 20
        
        elif event.key() == Qt.Key_Right:
            self.player_x += 20

    def paintEvent(self, event):
        painter = QPainter(self)

        #Draw Player
        painter.drawEllipse(
            self.player_x,
            self.player_y,
            self.player_size,
            self.player_size
        )

        #Draw Cars
        for car in self.cars:
            painter.drawRect(
                car["x"],
                car["y"],
                car["width"],
                car["height"]
            )

        #Draw Level
        painter.drawText(
            20,
            30,
            f"Level: {self.level}"
        )

app = QApplication(sys.argv)
game = TurtleCrossing()
game.show()
sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QInputDialog,
    QMessageBox
)
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import Qt


class USStatesGame(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("US States Game")
        self.setGeometry(100, 100, 800, 500)

        # Load map image
        self.map_image = QPixmap("us_map.png")

        # States list
        self.states = [
            "Alabama",
            "Alaska",
            "Arizona",
            "Arkansas",
            "California",
            "Colorado",
            "Connecticut",
            "Delaware",
            "Florida",
            "Georgia"
        ]

        # State positions
        self.state_positions = {
            "Alabama": (420, 250),
            "Alaska": (80, 420),
            "Arizona": (180, 280),
            "Arkansas": (380, 260),
            "California": (120, 220),
            "Colorado": (260, 200),
            "Connecticut": (650, 140),
            "Delaware": (620, 180),
            "Florida": (520, 360),
            "Georgia": (480, 280)
        }

        self.guessed_states = []

        self.ask_state()

    # Ask user for state input
    def ask_state(self):

        while len(self.guessed_states) < len(self.states):

            text, ok = QInputDialog.getText(
                self,
                "US States Game",
                f"{len(self.guessed_states)}/{len(self.states)} Correct\nEnter State Name:"
            )

            if not ok:
                break

            answer = text.title()

            if (
                answer in self.states
                and answer not in self.guessed_states
            ):

                self.guessed_states.append(answer)

                self.update()

        self.show_result()

    # Draw map and guessed states
    def paintEvent(self, event):

        painter = QPainter(self)

        # Draw map image
        painter.drawPixmap(0, 0, self.map_image)

        # Draw guessed states
        for state in self.guessed_states:

            x, y = self.state_positions[state]

            painter.drawText(x, y, state)

    # Final result
    def show_result(self):

        missing_states = []

        for state in self.states:

            if state not in self.guessed_states:
                missing_states.append(state)

        message = (
            f"Game Over!\n\n"
            f"Correct: {len(self.guessed_states)}\n\n"
            f"Missed States:\n"
            + "\n".join(missing_states)
        )

        QMessageBox.information(
            self,
            "Result",
            message
        )


app = QApplication(sys.argv)

game = USStatesGame()
game.show()

sys.exit(app.exec_())
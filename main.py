import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLineEdit
)
from PyQt5.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calculator")
        self.setFixedSize(350, 500)

        self.create_ui()
        self.apply_styles()

    def create_ui(self):
        main_layout = QVBoxLayout()

        # Display
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(70)

        main_layout.addWidget(self.display)

        # Button Layout
        grid = QGridLayout()

        buttons = [
            ("C", 0, 0),
            ("⌫", 0, 1),
            ("/", 0, 2),
            ("*", 0, 3),

            ("7", 1, 0),
            ("8", 1, 1),
            ("9", 1, 2),
            ("-", 1, 3),

            ("4", 2, 0),
            ("5", 2, 1),
            ("6", 2, 2),
            ("+", 2, 3),

            ("1", 3, 0),
            ("2", 3, 1),
            ("3", 3, 2),
            ("=", 3, 3, 2, 1),

            ("0", 5, 0, 1, 2),
            (".", 5, 2)
        ]

        for button in buttons:
            text = button[0]

            btn = QPushButton(text)
            btn.clicked.connect(self.button_clicked)

            if len(button) == 3:
                grid.addWidget(btn, button[1], button[2])
            else:
                grid.addWidget(
                    btn,
                    button[1],
                    button[2],
                    button[3],
                    button[4]
                )

        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    def button_clicked(self):
        button = self.sender()
        text = button.text()

        current = self.display.text()

        if text == "C":
            self.display.clear()

        elif text == "⌫":
            self.display.setText(current[:-1])

        elif text == "=":
            try:
                result = str(eval(current))
                self.display.setText(result)
            except:
                self.display.setText("Error")

        else:
            self.display.setText(current + text)

    def keyPressEvent(self, event):
        key = event.text()

        if key in "0123456789.+-*/":
            self.display.setText(self.display.text() + key)

        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            try:
                result = str(eval(self.display.text()))
                self.display.setText(result)
            except:
                self.display.setText("Error")

        elif event.key() == Qt.Key_Backspace:
            self.display.setText(self.display.text()[:-1])

        elif event.key() == Qt.Key_Escape:
            self.display.clear()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }

            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 28px;
            }

            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 20px;
                min-height: 60px;
            }

            QPushButton:hover {
                background-color: #4d4d4d;
            }

            QPushButton:pressed {
                background-color: #5f5f5f;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calculator()
    window.show()

    sys.exit(app.exec_())
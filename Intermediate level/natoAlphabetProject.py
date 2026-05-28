import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QVBoxLayout
)

class NATOAlphabet(QWidget):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NATO Alphabet Converter")
        self.setGeometry(100, 100, 500, 400)

        # NATO Dictionary
        self.nato = {
            "A": "Alpha",
            "B": "Bravo",
            "C": "Charlie",
            "D": "Delta",
            "E": "Echo",
            "F": "Foxtrot",
            "G": "Golf",
            "H": "Hotel",
            "I": "India",
            "J": "Juliett",
            "K": "Kilo",
            "L": "Lima",
            "M": "Mike",
            "N": "November",
            "O": "Oscar",
            "P": "Papa",
            "Q": "Quebec",
            "R": "Romeo",
            "S": "Sierra",
            "T": "Tango",
            "U": "Uniform",
            "V": "Victor",
            "W": "Whiskey",
            "X": "X-ray",
            "Y": "Yankee",
            "Z": "Zulu"
        }

        # Widgets
        self.title_label = QLabel("Enter a word: ")

        self.input_box = QLineEdit()

        self.convert_button = QPushButton("Convert")

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        # Layout
        layout = QVBoxLayout()

        layout.addWidget(self.title_label)
        layout.addWidget(self.input_box)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.output_box)

        self.setLayout(layout)

        # Button event
        self.convert_button.clicked.connect(self.convert_word)

    # Convert Function
    def convert_word(self):

        word = self.input_box.text().upper()

        result = []

        for letter in word:
            if letter in self.nato:
                result.append(self.nato[letter])
        
        final_result = "\n".join(result)
        self.output_box.setText(final_result)

app = QApplication(sys.argv)
window = NATOAlphabet()
window.show()
sys.exit(app.exec_())
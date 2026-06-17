import sys
import random
from dataclasses import dataclass, field
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QButtonGroup,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


@dataclass
class Question:
    text: str
    answer: str
    options: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.answer not in self.options:
            self.options.append(self.answer)
        random.shuffle(self.options)


class QuizBrain:
    def __init__(self, questions: list[Question]):
        self._questions = questions
        self._index = 0
        self.score = 0

    @property
    def current(self) -> Optional[Question]:
        return self._questions[self._index] if self._index < len(self._questions) else None

    @property
    def has_next(self) -> bool:
        return self._index < len(self._questions)

    def submit(self, choice: str) -> bool:
        if not self.current:
            return False
        correct = choice.strip().lower() == self.current.answer.strip().lower()
        if correct:
            self.score += 1
        self._index += 1
        return correct

    def progress(self) -> str:
        return f"Question {self._index + 1} of {len(self._questions)}"

    def restart(self):
        self._index = 0
        self.score = 0
        for q in self._questions:
            random.shuffle(q.options)


class QuizWindow(QMainWindow):
    DARK_BG = "#2b2b2b"
    CARD_BG = "#3c3f41"
    TEXT_FG = "#f0f0f0"
    MUTED_FG = "#aaaaaa"
    CORRECT_FG = "#6aab73"
    WRONG_FG = "#cc6666"
    BTN_HOVER = "#5a5c5e"
    GREEN_BTN = "#6aab73"
    GREEN_HOVER = "#5c9a65"

    def __init__(self, questions: list[Question], title: str = "Quiz App"):
        super().__init__()
        self.brain = QuizBrain(questions)

        self.setWindowTitle(title)
        self.setFixedSize(600, 420)
        self.setStyleSheet(f"QMainWindow {{ background-color: {self.DARK_BG}; }}")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(10)

        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.question_label.setStyleSheet(f"color: {self.TEXT_FG}; padding: 10px;")
        layout.addWidget(self.question_label)

        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setFont(QFont("Segoe UI", 10))
        self.progress_label.setStyleSheet(f"color: {self.MUTED_FG};")
        layout.addWidget(self.progress_label)

        self.feedback_label = QLabel()
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setFont(QFont("Segoe UI", 11, QFont.StyleItalic))
        self.feedback_label.setStyleSheet(f"color: {self.MUTED_FG};")
        layout.addWidget(self.feedback_label)

        self.btn_group = QButtonGroup()
        self.buttons: list[QPushButton] = []
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        for i in range(4):
            btn = QPushButton()
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 12))
            btn.setStyleSheet(self._btn_style())
            btn.clicked.connect(lambda checked, idx=i: self._on_click(idx))
            self.btn_group.addButton(btn, i)
            btn_layout.addWidget(btn)
            self.buttons.append(btn)
        layout.addLayout(btn_layout)

        layout.addStretch()
        self._show_question()

    def _btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {self.CARD_BG};
                color: {self.TEXT_FG};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {self.BTN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #4a4c4e;
            }}
            QPushButton:disabled {{
                background-color: #2a2a2a;
                color: #666666;
            }}
        """

    def _show_question(self):
        q = self.brain.current
        if not q:
            self._end_quiz()
            return

        self.question_label.setText(q.text)
        self.progress_label.setText(self.brain.progress())
        self.feedback_label.setText("")

        for btn, option in zip(self.buttons, q.options):
            btn.setText(f"  {option}")
            btn.setEnabled(True)
        for btn in self.buttons[len(q.options):]:
            btn.setText("")
            btn.setEnabled(False)

    def _on_click(self, idx: int):
        q = self.brain.current
        if not q or idx >= len(q.options):
            return

        choice = q.options[idx]
        correct = self.brain.submit(choice)

        for btn in self.buttons:
            btn.setEnabled(False)

        if correct:
            self.feedback_label.setText("Correct!")
            self.feedback_label.setStyleSheet(f"color: {self.CORRECT_FG};")
        else:
            self.feedback_label.setText(f"Incorrect. The answer was: {q.answer}")
            self.feedback_label.setStyleSheet(f"color: {self.WRONG_FG};")

        QTimer.singleShot(1500, self._show_question)

    def _end_quiz(self):
        total = len(self.brain._questions)
        score = self.brain.score
        pct = round(score / total * 100)

        self.question_label.setText(f"Quiz Complete!\n\nScore: {score}/{total}  ({pct}%)")
        self.progress_label.setText("")
        self.feedback_label.setText("")

        for btn in self.buttons:
            btn.setText("")
            btn.setEnabled(False)

        self.restart_btn = QPushButton("Play Again")
        self.restart_btn.setMinimumHeight(40)
        self.restart_btn.setCursor(Qt.PointingHandCursor)
        self.restart_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.restart_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.GREEN_BTN};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
            }}
            QPushButton:hover {{
                background-color: {self.GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #4d8a56;
            }}
        """)
        self.restart_btn.clicked.connect(self._restart)

        layout = self.centralWidget().layout()
        layout.insertWidget(layout.count() - 1, self.restart_btn)

    def _restart(self):
        self.restart_btn.deleteLater()
        self.restart_btn = None
        self.brain.restart()
        self._show_question()


def sample_questions() -> list[Question]:
    return [
        Question("What is the capital of France?", "Paris",
                 ["London", "Berlin", "Madrid"]),
        Question("Which planet is known as the Red Planet?", "Mars",
                 ["Venus", "Jupiter", "Saturn"]),
        Question("Who wrote 'Romeo and Juliet'?", "William Shakespeare",
                 ["Charles Dickens", "Mark Twain", "Jane Austen"]),
        Question("What is the chemical symbol for water?", "H2O",
                 ["CO2", "O2", "NaCl"]),
        Question("Which year did World War II end?", "1945",
                 ["1939", "1941", "1944"]),
    ]


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = QuizWindow(sample_questions(), "General Knowledge Quiz")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

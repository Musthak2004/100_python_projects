class Question:

    def __init__(self, text, answer):

        self.text = text
        self.answer = answer


class QuizBrain:

    def __init__(self, question_list):

        self.question_number = 0
        self.score = 0
        self.question_list = question_list

    # Check if questions still exist
    def still_has_questions(self):

        return self.question_number < len(self.question_list)

    # Ask next question
    def next_question(self):

        current_question = self.question_list[self.question_number]

        user_answer = input(
            f"\nQ.{self.question_number + 1}: "
            f"{current_question.text} (True/False): "
        ).lower()

        self.check_answer(user_answer, current_question.answer)

        self.question_number += 1

    # Check answer
    def check_answer(self, user_answer, correct_answer):

        if user_answer == correct_answer.lower():

            print("Correct!")

            self.score += 1

        else:

            print("Wrong!")

        print(f"Correct Answer: {correct_answer}")
        print(f"Current Score: {self.score}/{self.question_number + 1}")


# Question Data
question_data = [

    {"text": "Python is a programming language.", "answer": "True"},

    {"text": "The Earth is flat.", "answer": "False"},

    {"text": "2 + 2 = 4.", "answer": "True"},

    {"text": "Java was created before Python.", "answer": "True"},

    {"text": "HTML is a programming language.", "answer": "False"}
]


# Create Question Objects
question_bank = []

for question in question_data:

    question_text = question["text"]
    question_answer = question["answer"]

    new_question = Question(question_text, question_answer)

    question_bank.append(new_question)


# Create Quiz Object
quiz = QuizBrain(question_bank)


# Start Quiz
print("===== QUIZ GAME =====")

while quiz.still_has_questions():

    quiz.next_question()


print("\n===== QUIZ FINISHED =====")
print(f"Final Score: {quiz.score}/{len(question_bank)}")
import os
from abc import ABC, abstractmethod
from functools import reduce

import streamlit as st
from PIL import Image


class BaseQuestion(ABC):
    #Parent class for question type A & B

    def __init__(self, qid, correct_answer, text, choices, qtype):
        self.qid = qid
        self.correct_answer = correct_answer
        self.text = text
        self.choices = choices
        self.qtype = qtype

    @abstractmethod
    def show_extra_content(self):
        pass

    def render(self, position, total):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.header(f"Question {self.qid}")
        with col2:
            st.write(f"Question {position + 1} of {total}")

        st.markdown(self.qtype)
        st.subheader(self.text)
        self.show_extra_content()


class TypeAQuestion(BaseQuestion):
    def show_extra_content(self):
        return None


class TypeBQuestion(BaseQuestion):
    def show_extra_content(self):
        image_path = f"images/Q{self.qid}.jpg"
        if os.path.exists(image_path):
            st.image(Image.open(image_path), width=300)
        else:
            st.warning(f"Image not found: {image_path}")


class QuestionFactory:
    #Creates the correct object for Type A or Type B

    @staticmethod
    def create_from_line(line):
        parts = line.split(":")
        qid, correct_answer, text = parts[0], parts[1], parts[2]
        choices = parts[3:7]
        qtype = parts[7]

        if qtype == "Type B":
            return TypeBQuestion(qid, correct_answer, text, choices, qtype)
        return TypeAQuestion(qid, correct_answer, text, choices, qtype)


class QuizFileManager:
    QUESTIONS_FILE = "Questions.txt"
    ANSWERS_FILE = "Answers.txt"

    @classmethod
    def load_questions(cls):
        try:
            with open(cls.QUESTIONS_FILE, "r", encoding="utf-8") as file:
                lines = file.readlines()

            # filter: remove empty lines
            non_empty_lines = list(filter(lambda line: line.strip(), lines))
            # map: convert each line into a question object
            return list(map(lambda line: QuestionFactory.create_from_line(line.strip()), non_empty_lines))
        except FileNotFoundError:
            st.error("Questions.txt could not be loaded!")
            return []

    @classmethod
    def save_user_answers(cls, questions, user_answers, user_name):
        total_questions = len(questions)
        user_score = QuizScorer.recursive_score(questions, user_answers)
        percentage = (user_score / total_questions) * 100 if total_questions else 0

        header = ["Name"] + list(map(lambda i: f"Q{i+1}", range(total_questions))) + ["Score", "Percentage"]
        user_row = [user_name] + list(map(lambda i: user_answers.get(i, ""), range(total_questions)))
        user_row += [str(user_score), f"{percentage:.2f}"]

        try:
            with open(cls.ANSWERS_FILE, "r", encoding="utf-8") as file:
                file_empty = file.read().strip() == ""
        except FileNotFoundError:
            file_empty = True

        with open(cls.ANSWERS_FILE, "a", encoding="utf-8") as file:
            if file_empty:
                file.write("\t".join(header) + "\n")
            file.write("\t".join(user_row) + "\n")


class QuizScorer:
    @staticmethod
    # recursive to calculate particepant score
    def recursive_score(questions, user_answers, index=0):
        if index >= len(questions):
            return 0
        current_score = 1 if user_answers.get(index) == questions[index].correct_answer else 0
        return current_score + QuizScorer.recursive_score(questions, user_answers, index + 1)

    @staticmethod
    def reduce_score(questions, user_answers):
        # overloaded version of reduce_score() using reduce 
        return reduce(
            lambda total, item: total + (1 if user_answers.get(item[0]) == item[1].correct_answer else 0),
            enumerate(questions),
            0,
        )


class QuizUI:
    answer_to_letter = staticmethod(lambda selected_option: selected_option[0])

    @staticmethod
    def show_start_screen():
        st.title("Knowledge Test")
        st.header("To start the quiz please insert your name and click start button")
        st.session_state.user_name = st.text_input("Enter your name")

        if st.button("Start Quiz"):
            if not st.session_state.user_name.strip():
                st.error("Name is required")
            else:
                st.session_state.quiz_started = True
                st.session_state.questions = QuizFileManager.load_questions()
                st.rerun()

    @staticmethod
    def show_navigation_bar():
        with st.form("main_form"):
            if st.form_submit_button("To Main Menu"):
                st.session_state.quiz_started = False
                st.session_state.question_index = 0
                st.session_state.answers = {}
                st.session_state.page = "quiz"
                st.rerun()
            st.write(f"**Name:** {st.session_state.user_name}")

    @staticmethod
    def show_question(question, question_index, total):
        QuizUI.show_navigation_bar()

        with st.form("quiz_form"):
            question.render(question_index, total)

            saved_answer = st.session_state.answers.get(question_index, "A")
            radio_index = ord(saved_answer) - ord("A")

            selected_option = st.radio(
                "",
                question.choices,
                index=radio_index,
                key=f"radio_{question_index}",
            )

            st.session_state.answers[question_index] = QuizUI.answer_to_letter(selected_option)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if question_index > 0 and st.form_submit_button("Previous"):
                    st.session_state.question_index -= 1
                    st.rerun()

            with col2:
                last_question = question_index == total - 1
                if not last_question and st.form_submit_button("Next"):
                    st.session_state.question_index += 1
                    st.rerun()
                elif last_question and st.form_submit_button("Submit"):
                    QuizFileManager.save_user_answers(
                        st.session_state.questions,
                        st.session_state.answers,
                        st.session_state.user_name,
                    )
                    st.session_state.page = "result"
                    st.rerun()


class QuizApp:
    def run(self):
        if not st.session_state.quiz_started:
            QuizUI.show_start_screen()
            return

        questions = st.session_state.questions
        current_index = st.session_state.question_index
        QuizUI.show_question(questions[current_index], current_index, len(questions))


# keep compatibility with Main.py and MyResult.py
load_questions = QuizFileManager.load_questions


def main():
    QuizApp().run()

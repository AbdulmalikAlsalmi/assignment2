from functools import reduce

import pandas as pd
import streamlit as st
import MyQuiz


class ResultFileManager:
    @staticmethod
    def read_answers_file():
        try:
            with open("Answers.txt", "r", encoding="utf-8") as file:
                return list(filter(lambda line: line.strip(), file.readlines()))
        except FileNotFoundError:
            st.error("Answers.txt could not be loaded!")
            return []


class ResultBuilder:
    @staticmethod
    def get_latest_record():
        records = ResultFileManager.read_answers_file()
        if len(records) <= 1:
            return []
        return records[-1].strip().split("\t")

    @staticmethod
    def build_summary_rows(questions, user_record):
        def to_row(item):
            index, question = item
            participant_answer = user_record[index + 1]
            result = "Correct" if participant_answer == question.correct_answer else "Wrong"
            return {
                "Question": f"Q{question.qid}",
                "Your Answer": participant_answer,
                "Correct Answer": question.correct_answer,
                "Result": result,
            }

        return list(map(to_row, enumerate(questions)))

    @staticmethod
    def total_correct(summary_rows):
        return reduce(lambda total, row: total + (1 if row["Result"] == "Correct" else 0), summary_rows, 0)


class ResultUI:
    @staticmethod
    def show_participant_info(user_name, user_score, total_questions, user_percentage):
        st.subheader("Participant Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Name:** {user_name}")
        with col2:
            st.write(f"**Total Score:** {user_score}/{total_questions}")
        with col3:
            st.write(f"**Percentage:** {user_percentage}%")

    @staticmethod
    def show_summary_table(summary_rows):
        st.subheader("Summary Table")
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    @staticmethod
    def show_quit_button():
        if st.button("Quit"):
            st.session_state.quiz_started = False
            st.session_state.question_index = 0
            st.session_state.answers = {}
            st.session_state.questions = []
            st.session_state.page = "quiz"
            st.rerun()


class ResultApp:
    def run(self):
        st.title("Answer Page")
        st.success("Thank you for taking the survey!")

        user_record = ResultBuilder.get_latest_record()
        if not user_record:
            st.warning("No participant result found yet.")
            return

        questions = st.session_state.get("questions", [])
        if not questions:
            questions = MyQuiz.load_questions()
            st.session_state.questions = questions

        total_questions = len(questions)
        user_name = user_record[0]
        user_score = user_record[-2]
        user_percentage = user_record[-1]

        ResultUI.show_participant_info(user_name, user_score, total_questions, user_percentage)
        st.divider()

        summary_rows = ResultBuilder.build_summary_rows(questions, user_record)
        ResultUI.show_summary_table(summary_rows)
        st.divider()
        ResultUI.show_quit_button()


def main():
    ResultApp().run()

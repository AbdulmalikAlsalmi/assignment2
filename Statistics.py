from functools import reduce

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


class StatisticsRepository:
    @staticmethod
    def load_answers_file():
        try:
            return pd.read_csv("Answers.txt", sep="\t")
        except FileNotFoundError:
            return pd.DataFrame()
        except Exception as error:
            st.error(f"Error reading Answers.txt: {error}")
            return pd.DataFrame()

    @staticmethod
    def load_correct_answers():
        try:
            with open("Questions.txt", "r", encoding="utf-8") as file:
                lines = list(filter(lambda line: line.strip(), file.readlines()))

            def to_pair(line):
                parts = line.strip().split(":")
                return (f"Q{parts[0]}", parts[1])

            return dict(map(to_pair, lines))
        except FileNotFoundError:
            st.error("Questions.txt could not be loaded!")
            return {}


class StatisticsCalculator:
    @staticmethod
    def question_columns(df):
        return list(filter(lambda col: str(col).startswith("Q"), df.columns))

    @staticmethod
    def calculate_row_score(row, question_columns, correct_answers):
        values = map(
            lambda q: 1 if str(row[q]).strip() == str(correct_answers.get(q, "")).strip() else 0,
            question_columns,
        )
        return reduce(lambda total, mark: total + mark, values, 0)

    @staticmethod
    def participant_scores(df, correct_answers):
        question_columns = StatisticsCalculator.question_columns(df)
        return [
            {
                "Name": row["Name"],
                "Total Score": StatisticsCalculator.calculate_row_score(row, question_columns, correct_answers),
            }
            for _, row in df.iterrows()
        ]

    @staticmethod
    def question_totals(df, correct_answers):
        question_columns = StatisticsCalculator.question_columns(df)
        results = []

        for q in question_columns:
            marks = map(
                lambda value: 1 if str(value).strip() == str(correct_answers.get(q, "")).strip() else 0,
                df[q],
            )
            results.append({
                "Question": q,
                "Total Marks Obtained": reduce(lambda total, mark: total + mark, marks, 0)
            })

        return results

    @staticmethod
    def whole_quiz_total(question_totals):
        return reduce(lambda total, item: total + item["Total Marks Obtained"], question_totals, 0)

    @staticmethod
    def build_quiz_matrix(df, correct_answers):
        """Build matrix similar to the sample image.
        Shows each participant, all answers, score, and percentage.
        """
        question_columns = StatisticsCalculator.question_columns(df)
        total_questions = len(question_columns)

        matrix_rows = []
        for _, row in df.iterrows():
            score = StatisticsCalculator.calculate_row_score(row, question_columns, correct_answers)
            percentage = round((score / total_questions) * 100, 2) if total_questions else 0.0

            matrix_row = {"Name": row["Name"]}
            matrix_row.update({q: row[q] for q in question_columns})
            matrix_row["Score"] = score
            matrix_row["Percentage"] = percentage
            matrix_rows.append(matrix_row)

        return pd.DataFrame(matrix_rows)


    @staticmethod
    def chart_data(matrix_df):
        chart_df = matrix_df[["Name", "Percentage"]].copy()
        overall_percentage = round(chart_df["Percentage"].mean(), 2) if not chart_df.empty else 0.0
        overall_row = pd.DataFrame([{"Name": "All", "Percentage": overall_percentage}])
        return pd.concat([overall_row, chart_df], ignore_index=True)

    @staticmethod
    def summary_statistics(series, label):
        if series.empty:
            return {
                "Mean": 0,
                "Median": 0,
                "Mode": 0,
                "Lowest": 0,
                "Highest": 0,
                "Label": label,
            }

        mode_value = series.mode()
        return {
            "Mean": round(series.mean(), 4),
            "Median": round(series.median(), 4),
            "Mode": round(mode_value.iloc[0], 4) if not mode_value.empty else 0,
            "Lowest": round(series.min(), 4),
            "Highest": round(series.max(), 4),
            "Label": label,
        }


class StatisticsUI:
    @staticmethod
    def show_overview(matrix_df):
        total_records = len(matrix_df)
        total_elements = matrix_df.shape[0] * matrix_df.shape[1]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("No. of elements", total_elements)
        with col2:
            st.metric("No. of records", total_records)

    @staticmethod
    def show_summary_box(stats):
        st.markdown(
            f"""
            <div style="background-color:#1f1f1f; color:#f5f5f5; padding:20px; border-radius:10px; margin-bottom:16px;">
                <h4 style="margin-top:0; text-align:center;">{stats['Label'].upper()}</h4>
                <p>Mean value for {stats['Label']}: <b>{stats['Mean']}</b></p>
                <p>Median value for {stats['Label']}: <b>{stats['Median']}</b></p>
                <p>Mode value for {stats['Label']}: <b>{stats['Mode']}</b></p>
                <br>
                <p>Lowest {stats['Label']}: <b>{stats['Lowest']}</b></p>
                <p>Highest {stats['Label']}: <b>{stats['Highest']}</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def show_quiz_matrix(matrix_df):
        st.subheader("Quiz Matrix Results")
        matrix_df["Score"] = matrix_df["Score"].astype(str)
        matrix_df["Percentage"] = matrix_df["Percentage"].astype(str)
        st.dataframe(matrix_df, use_container_width=True, hide_index=True)


    @staticmethod
    def show_bar_chart(chart_df):
        st.subheader("Performance Bar Chart")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(chart_df["Name"], chart_df["Percentage"])
        ax.set_xlabel("Name")
        ax.set_ylabel("Percentage")
        ax.set_ylim(0, 105)
        plt.xticks(rotation=90)
        plt.tight_layout()
        st.pyplot(fig)

    @staticmethod
    def show_detailed_statistics(participant_scores, question_totals, whole_quiz_total, total_answers):
        st.subheader("Other Statistics")

        st.markdown("**1. Individual Total Marks**")
        participant_df = pd.DataFrame(participant_scores)
        participant_df["Total Score"] = participant_df["Total Score"].astype(str)
        st.dataframe(participant_df, use_container_width=True, hide_index=True)

        st.markdown("**2. Total Marks Obtained by All Participants Per Question**")
        question_df = pd.DataFrame(question_totals)
        question_df["Total Marks Obtained"] = question_df["Total Marks Obtained"].astype(str)
        st.dataframe(question_df, use_container_width=True, hide_index=True)

        st.markdown("**3. Total Marks Obtained by All Participants for the Whole Quiz**")
        st.metric("Whole Quiz Total Marks", whole_quiz_total)
        average = str(whole_quiz_total/total_answers)
        st.metric("Average:", f"{float(average):.2f}")

class StatisticsApp:
    def run(self):
        st.title("Quiz Statistics")

        df = StatisticsRepository.load_answers_file()
        correct_answers = StatisticsRepository.load_correct_answers()

        if df.empty:
            st.warning("No participant records found yet.")
            return

        participant_scores = StatisticsCalculator.participant_scores(df, correct_answers)
        question_totals = StatisticsCalculator.question_totals(df, correct_answers)
        whole_quiz_total = StatisticsCalculator.whole_quiz_total(question_totals)

        matrix_df = StatisticsCalculator.build_quiz_matrix(df, correct_answers)
        score_stats = StatisticsCalculator.summary_statistics(matrix_df["Score"], "Score")
        percentage_stats = StatisticsCalculator.summary_statistics(matrix_df["Percentage"], "Percentage")
        chart_df = StatisticsCalculator.chart_data(matrix_df)

        StatisticsUI.show_overview(matrix_df)
        st.divider()

        left_col, right_col = st.columns([3, 1])

        with left_col:
            StatisticsUI.show_quiz_matrix(matrix_df)

        with right_col:
            StatisticsUI.show_summary_box(score_stats)
            StatisticsUI.show_summary_box(percentage_stats)

        st.divider()
        StatisticsUI.show_bar_chart(chart_df)

        st.divider()
        StatisticsUI.show_detailed_statistics(participant_scores, question_totals, whole_quiz_total, len(df))



def main():
    StatisticsApp().run()

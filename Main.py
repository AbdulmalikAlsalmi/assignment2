import streamlit as st
from streamlit_option_menu import option_menu
import MyQuiz
import MyResult
import Statistics


class AppState:
    #Initialize and reset Streamlit session state
    DEFAULTS = {
        "page": "quiz",
        "question_index": 0,
        "answers": {},
        "quiz_started": False,
        "user_name": "",
        "questions": [],
    }

    @classmethod
    def init(cls):
        for key, value in cls.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @classmethod
    def reset_quiz(cls):
        st.session_state.question_index = 0
        st.session_state.answers = {}
        st.session_state.quiz_started = False
        st.session_state.page = "quiz"
        st.session_state.questions = []


class HomePage:
    @staticmethod
    def show():
        st.title("Welcome to F&B Research Programme")
        st.header("This system analyzes Malaysians’ knowledge about food and its origin.")
        st.write(
            "The purpose of it is to analyse Malaysians’ food knowledge and its origin, "
            "before launching a new food product on the market."
        )
        st.write("Please select an option from side bar navigation.")


class NavigationApp:
    def run(self):
        st.set_page_config(page_title="F&B Research App", layout="wide")
        AppState.init()

        with st.sidebar:
            selected = option_menu(
                menu_title="Main Menu",
                options=["Home", "Survey", "My Result", "Statistics"],
                icons=["bi bi-app", "clipboard", "info-circle", "bar-chart"],
                menu_icon="bi bi-list",
                default_index=0,
            )

        if selected == "Home":
            HomePage.show()
        elif selected == "Survey":
            if st.session_state.page == "quiz":
                MyQuiz.main()
            else:
                MyResult.main()
        elif selected == "My Result":
            MyResult.main()
        elif selected == "Statistics":
            Statistics.main()


NavigationApp().run()


import os

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

from questions import QUESTIONS
from database import run_query


load_dotenv()

st.set_page_config(
    page_title="Sephora SQL Lab",
    page_icon="✿",
    layout="wide"
)

st.title("⋆˙⟡ Sephora SQL Lab")
st.caption(
    "SQL interview practice with real Sephora products "
    "and 10,000 sampled reviews."
)
st.divider()

# -----------------------------------
# Authentication
# -----------------------------------

# Each browser session gets its own Supabase client.
if "supabase_client" not in st.session_state:
    st.session_state.supabase_client = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"]
    )

supabase = st.session_state.supabase_client

if "user_session" not in st.session_state:
    st.session_state.user_session = None

if "answers" not in st.session_state:
    st.session_state.answers = {}


def save_answer(user_id, question_id, query):
    response = supabase.table("quiz_answers").upsert(
        {
            "user_id": user_id,
            "question_id": question_id,
            "sql_answer": query,
        },
        on_conflict="user_id,question_id",
    ).execute()

    return response



def authenticated_user():
    session = st.session_state.user_session

    if session is None:
        return None

    try:
        response = supabase.auth.get_user(
            session.access_token
        )
        return response.user

    except Exception:
        st.session_state.user_session = None
        return None


user = authenticated_user()

if user is None:
    st.subheader("Sign in to begin")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password"
        )

        st.divider()

        st.markdown("#### Grader Access")

        st.info(
            "A dedicated grader account has been created.\n\n"
            "**Email:** grader@example.com\n\n"
            "The password is provided separately through the private "
            "Canvas submission."
)


        submitted = st.form_submit_button("Sign In")


    if submitted:
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            st.session_state.user_session = response.session
            st.session_state.answers = {}
            st.session_state.pop("answers_loaded_for", None)
            st.rerun()
            

        except Exception:
            st.error("Sign-in failed. Check your credentials.")

    st.info(
        "You must sign in to run SQL queries "
        "or save your answers."
    )

    st.stop()


# Load saved answers once per authenticated user.
if st.session_state.get("answers_loaded_for") != user.id:
    try:
        response = (
            supabase.table("quiz_answers")
            .select("question_id, sql_answer")
            .eq("user_id", user.id)
            .execute()
        )

        st.session_state.answers = {
            row["question_id"]: row["sql_answer"]
            for row in response.data
        }

        # Reset editor values to match this user's saved work.
        for q in QUESTIONS:
            st.session_state.pop(f"sql_{q['id']}", None)

        st.session_state.answers_loaded_for = user.id

    except Exception as error:
        st.error(f"Could not load saved answers: {error}")
        st.stop()


# -----------------------------------
# Sidebar
# -----------------------------------

with st.sidebar:
    st.success(f"Signed in as {user.email}")

    if st.button("Sign Out"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.user_session = None
        st.session_state.answers = {}
        st.session_state.pop("answers_loaded_for", None)
        # Clear SQL editor values from the previous user.
        for question in QUESTIONS:
            st.session_state.pop(
                f"sql_{question['id']}", None
            )

        st.rerun()

    st.divider()

    st.subheader("Quiz Overview")
    st.write("5 questions")
    st.write("4 points each")
    st.write("20 points total")

    st.caption(
        "Review questions use a sample of "
        "10,000 Sephora reviews."
    )

st.subheader("Database Reference")
st.caption("Available tables and columns")

with st.expander("products"):
    st.code(
        """product_id          TEXT (PK)
product_name        TEXT
brand_name          TEXT
price_usd           NUMERIC
rating              NUMERIC
loves_count         INTEGER
primary_category    TEXT
secondary_category  TEXT
sephora_exclusive   BOOLEAN""",
        language="text"
    )

with st.expander("reviews"):
    st.code(
        """review_id        BIGINT (PK)
product_id       TEXT (FK)
author_id        TEXT
rating           INTEGER
is_recommended   BOOLEAN
submission_time  DATE
review_text      TEXT
skin_type        TEXT""",
        language="text"
    )

st.caption(
    "Relationship: reviews.product_id "
    "references products.product_id"
)


# -----------------------------------
# Question selection
# -----------------------------------


# -----------------------------------
# Question selection
# -----------------------------------

st.markdown("""
<style>
div[data-testid="stSelectbox"] {
    background-color: #FFF0F5;
    padding: 18px;
    border: 2px solid #E78BAA;
    border-radius: 12px;
}

div[data-testid="stSelectbox"] label p {
    color: #AD4269;
    font-size: 18px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

selected_id = st.selectbox(
    "Choose a question",
    options=[q["id"] for q in QUESTIONS],
    format_func=lambda i: (
        f"Question {i}: {QUESTIONS[i - 1]['title']}"
    )
)


question = QUESTIONS[selected_id - 1]

st.divider()

st.subheader(
    f"Question {question['id']}: {question['title']}"
)

st.caption(
    f"{question['difficulty']} | "
    f"{question['points']} points | "
    f"{question['pattern']}"
)

st.write(question["prompt"])

# -----------------------------------
# Hint and reference solution
# -----------------------------------

with st.expander("Show Hint"):
    st.info(question["hint"])


with st.expander("Show Expected SQL & Results"):
    st.write("Reference SQL solution:")
    st.code(question["solution"], language="sql")

    st.write("Expected result:")
    st.write(question["expected"])

    # if st.button(
    #     "Show Expected Output Rows",
    #     key=f"expected_{question['id']}"
    # ):
    #     try:
    #         expected_df = run_query(question["solution"])
    #         st.dataframe(expected_df, use_container_width=True)
    #     except Exception as e:
    #         st.error(f"Could not load expected results: {e}")




# -----------------------------------
# SQL editor
# -----------------------------------

st.subheader("Your SQL Query")

answer_key = f"sql_{question['id']}"

if answer_key not in st.session_state:
    st.session_state[answer_key] = (
        st.session_state.answers.get(
            question["id"], ""
        )
    )

query = st.text_area(
    "Write your SQL below:",
    key=answer_key,
    height=200,
    placeholder="SELECT ..."
)


# -----------------------------------
# Run and save buttons
# -----------------------------------

col1, col2 = st.columns(2)

with col1:
    run_clicked = st.button(
        "▶ Run Query",
        use_container_width=True
    )

with col2:
    save_clicked = st.button(
        "Save Answer",
        use_container_width=True
    )


# -----------------------------------
# Execute SQL
# -----------------------------------

if run_clicked:

    if authenticated_user() is None:
        st.error(
            "Your session has expired. "
            "Please sign in again."
        )
        st.stop()

    try:
        result = run_query(query)

        st.success(
            f"Query executed successfully! "
            f"{len(result)} row(s) returned."
        )

        st.subheader("Query Results")

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

    except Exception as error:
        st.error(f"Query failed: {error}")


# -----------------------------------
# Save answer
# -----------------------------------


if save_clicked:

    current_user = authenticated_user()

    if current_user is None:
        st.error(
            "Your session has expired. "
            "Please sign in again."
        )
        st.stop()

    if not query.strip():
        st.warning("Please write a SQL query before saving.")

    else:
        try:
            save_answer(
                user_id=current_user.id,
                question_id=question["id"],
                query=query,
            )

            st.session_state.answers[question["id"]] = query

            st.success("Answer saved to Supabase!")

        except Exception as error:
            st.error(f"Could not save answer: {error}")



# -----------------------------------
# Progress
# -----------------------------------

st.divider()

saved_count = len(st.session_state.answers)

st.write(f"**Answers saved to Supabase: {saved_count} / 5**")

st.progress(saved_count / 5)

st.caption(
    "Your saved answers are stored securely in Supabase "
    "and will be available when you sign in again."
)

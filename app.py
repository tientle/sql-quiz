import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

st.set_page_config(
    page_title="Sephora SQL Lab",
    page_icon="💄",
    layout="wide"
)

@st.cache_resource
def get_supabase():
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"]
    )

supabase = get_supabase()

st.title("Sephora SQL Lab")
st.write("Practice SQL using real Sephora products and reviews!")

# Track authentication for this browser session
if "user_session" not in st.session_state:
    st.session_state.user_session = None

if st.session_state.user_session is None:

    st.subheader("Sign in to continue")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")

    if submitted:
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            st.session_state.user_session = response.session
            st.rerun()

        except Exception:
            st.error("Sign-in failed. Check your credentials.")

else:
    st.success("You're signed in!")

    if st.button("Sign Out"):
        st.session_state.user_session = None
        st.rerun()

    st.subheader("Your SQL Quiz")
    st.write("Quiz questions will appear here.")
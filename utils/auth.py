import streamlit as st

def validate_customer_id(customer_id: str) -> bool:
    """
    Basic validation logic for customer ID.
    Args:
        customer_id (str): The ID entered by the user.
    Returns:
        bool: True if valid, False otherwise.
    """
    if not customer_id:
        return False
    if not customer_id.isdigit():
        return False
    # Add more validation logic if needed.
    return True

def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "customer_id" not in st.session_state:
        st.session_state.customer_id = ""

def login_customer(customer_id: str):
    if validate_customer_id(customer_id):
        st.session_state.logged_in = True
        st.session_state.customer_id = customer_id
        st.success(f"Logged in as Customer {customer_id}")
    else:
        st.error("Invalid Customer ID. Please enter digits only.")

def logout():
    st.session_state.logged_in = False
    st.session_state.customer_id = ""
    st.success("Logged out successfully.")

import streamlit as st
from tabs.orders import render_orders_tab
from tabs.product_lookup import render_product_lookup_tab

st.set_page_config(page_title="Customer Portal", page_icon="🛒", layout="wide")

# Simple login form (you can replace with your auth)
def show_login_form():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Dummy auth: password must be empty string for testing, replace with real auth
        if username and password == "":
            st.session_state["logged_in"] = True
            st.session_state["customer_id"] = username
            st.rerun()
        else:
            st.error("Invalid username or password")

if not st.session_state.get("logged_in", False):
    show_login_form()
    st.stop()

# User logged in, show portal with tabs
st.title("🛍️ Customer Portal")

tab1, tab2 = st.tabs(["📋 My Orders", "🔍 Product Lookup"])

with tab1:
    render_orders_tab(st.session_state.customer_id)

with tab2:
    render_product_lookup_tab(st.session_state.customer_id)

import streamlit as st
import requests

def get_base_url():
    return st.secrets["azure"]["function_base_url"].rstrip("/")

def get_function_key():
    return st.secrets["azure"]["function_key"]

def get_headers():
    token = get_function_key()
    return {"Authorization": f"Bearer {token}"}

def test_api_connection():
    try:
        url = f"{get_base_url()}/health"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def get_orders(customer_id: str):
    base_url = st.secrets["azure"]["function_base_url"].rstrip("/")
    token = st.secrets["azure"]["function_key"]  # This is your BEARER_TOKEN

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "customer_id": customer_id
    }

    url = f"{base_url}/orders"

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("orders", [])
    else:
        st.error(f"Error fetching orders: {response.status_code}")
        return []

def get_customer(customer_id):
    try:
        url = f"{get_base_url()}/customers/{customer_id}"
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching customer info: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Exception fetching customer info: {e}")
        return None

def get_product_supplier(product_id):
    try:
        url = f"{get_base_url()}/products/{product_id}/supplier"
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching supplier info: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Exception fetching supplier info: {e}")
        return None
API_BASE_URL= st.secrets["azure"]["recommendation_url"].rstrip("/")
def get_recommendations(customer_id, product_names):
    """Get product recommendations based on purchase history"""
    try:
        url = f"{API_BASE_URL}/api/recommendations/customer"
        payload = {
            "customer_id": customer_id,
            "purchase_history": product_names
        }
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json().get('recommended_products', [])
        else:
            return []
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return []
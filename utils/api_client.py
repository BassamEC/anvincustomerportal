import streamlit as st
import requests
import json

def get_base_url():
    base_url = st.secrets["azure"]["function_base_url"].rstrip("/")
    # Ensure /api is included for Azure Functions
    if not base_url.endswith("/api"):
        base_url += "/api"
    return base_url

def get_function_key():
    return st.secrets["azure"]["function_key"]

def get_headers():
    token = get_function_key()
    return {"Authorization": f"Bearer {token}"}

def test_api_connection():
    try:
        url = f"{get_base_url()}/health"
        response = requests.get(url, headers=get_headers(), timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

def get_orders(customer_id: str):
    try:
        base_url = get_base_url()
        headers = get_headers()
        
        params = {"customer_id": customer_id}
        url = f"{base_url}/orders"
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("orders", [])
        else:
            st.error(f"Error fetching orders: {response.status_code} - {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        st.error(f"Request exception: {e}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return []

def get_customer(customer_id):
    try:
        url = f"{get_base_url()}/customers/{customer_id}"
        
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching customer info: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Exception fetching customer info: {e}")
        return None

def get_product_supplier(product_id):
    try:
        url = f"{get_base_url()}/products/{product_id}/supplier"
        
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching supplier info: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Exception fetching supplier info: {e}")
        return None

# Updated recommendations function
def get_recommendations(customer_id, product_names):
    """Get product recommendations based on purchase history"""
    try:
        api_base_url = st.secrets["azure"]["recommendation_url"].rstrip("/")
        url = f"{api_base_url}/api/recommendations/customer"
        
        payload = {
            "customer_id": customer_id,
            "purchase_history": product_names
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json().get('recommended_products', [])
        else:
            st.error(f"Error fetching recommendations: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
        return []
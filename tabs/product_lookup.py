import streamlit as st
import pandas as pd
import json
from utils.api_client import get_product_supplier

def render_product_lookup_tab(customer_id):
    st.title("🔍 Product Lookup")

    product_id = st.text_input("Product ID", placeholder="Enter product ID (e.g., PROD-12345)")

    if st.button("Search") and product_id:
        with st.spinner("🔍 Searching for supplier information..."):
            supplier_data = get_product_supplier(product_id)

        if supplier_data:
            try:
                if isinstance(supplier_data, str):
                    supplier_data = json.loads(supplier_data)

                if isinstance(supplier_data, dict):
                    if 'supplier' in supplier_data:
                        supplier_data = supplier_data['supplier']
                    elif 'Supplier' in supplier_data:
                        supplier_data = supplier_data['Supplier']

                st.success(f"✅ Supplier Found for Product ID: `{product_id}`")

                if isinstance(supplier_data, dict) and any(k in supplier_data for k in ['CompanyName', 'CompanyID', 'ContactName']):
                    st.subheader("📋 Supplier Information")

                    col1, col2 = st.columns(2)
                    with col1:
                        if 'CompanyName' in supplier_data:
                            st.write(f"**Company:** {supplier_data['CompanyName']}")
                        if 'CompanyID' in supplier_data:
                            st.write(f"**Company ID:** {supplier_data['CompanyID']}")
                        if 'ContactName' in supplier_data:
                            st.write(f"**Contact Person:** {supplier_data['ContactName']}")
                        if 'C_Phone' in supplier_data:
                            phone = supplier_data['C_Phone']
                            if isinstance(phone, (int, float)):
                                phone_str = str(int(phone))
                                if len(phone_str) == 10:
                                    formatted_phone = f"({phone_str[:3]}) {phone_str[3:6]}-{phone_str[6:]}"
                                else:
                                    formatted_phone = phone_str
                            else:
                                formatted_phone = str(phone)
                            st.write(f"**Phone:** {formatted_phone}")
                        if 'Fax' in supplier_data and supplier_data['Fax'] != 'Not Available':
                            st.write(f"**Fax:** {supplier_data['Fax']}")

                    with col2:
                        if 'C_City' in supplier_data:
                            st.write(f"**City:** {supplier_data['C_City']}")
                        if 'C_Country' in supplier_data:
                            st.write(f"**Country:** {supplier_data['C_Country']}")

                        other_fields = {k: v for k, v in supplier_data.items() 
                                        if k not in ['CompanyName', 'CompanyID', 'ContactName', 'C_Phone', 'Fax', 'C_City', 'C_Country']
                                        and v and v != 'Not Available'}

                        if other_fields:
                            st.markdown("**ℹ️ Additional Information**")
                            for key, value in other_fields.items():
                                formatted_key = key.replace('_', ' ').replace('C_', '').title()
                                st.write(f"**{formatted_key}:** {value}")

                else:
                    st.error("❌ Unexpected data format received")
                    st.write(supplier_data)

            except json.JSONDecodeError:
                st.error("❌ Invalid data format received from server")
            except Exception as e:
                st.error(f"❌ Failed to display supplier information - {str(e)}")

        else:
            st.warning(f"⚠️ No supplier data found for Product ID: `{product_id}`")

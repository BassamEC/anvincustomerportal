import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils.api_client import get_orders, get_recommendations

def render_orders_tab(customer_id):
    st.title("📋 My Orders")

    # Fetch orders for given customer_id
    raw_orders = get_orders(customer_id)

    if not raw_orders:
        st.info("📦 No orders found.")
        return

    cleaned_orders = []
    parsing_errors = 0

    for row in raw_orders:
        try:
            if isinstance(row, str):
                cleaned_orders.append(json.loads(row))
            elif isinstance(row, dict) and "data" in row:
                cleaned_orders.append(json.loads(row["data"]))
            else:
                cleaned_orders.append(row)
        except json.JSONDecodeError:
            parsing_errors += 1
            continue

    if parsing_errors > 0:
        st.warning(f"⚠️ {parsing_errors} item(s) could not be loaded properly.")

    df = pd.DataFrame(cleaned_orders)

    if df.empty:
        st.error("❌ No valid orders could be loaded.")
        return

    # Convert date columns to datetime
    for col in ['OrderDate', 'ShipDate', 'order_date', 'ship_date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Identify order ID column
    order_id_col = None
    for col in ['OrderID', 'OrderNumber', 'order_id', 'order_number']:
        if col in df.columns:
            order_id_col = col
            break

    if not order_id_col:
        st.error("No order ID column found in the data.")
        return

    orders_grouped = df.groupby(order_id_col)

    # Calculate summary metrics
    unique_orders = len(orders_grouped)
    total_items = len(df)

    order_summaries = []
    for order_id, order_items in orders_grouped:
        first_item = order_items.iloc[0]

        if 'Price' in order_items.columns and 'Quantity' in order_items.columns:
            order_total = (order_items['Price'] * order_items['Quantity']).sum()
        elif 'TotalAmount' in first_item:
            order_total = first_item['TotalAmount']
        else:
            order_total = 0

        order_summaries.append({
            'OrderID': order_id,
            'OrderDate': first_item.get('OrderDate', first_item.get('order_date')),
            'Status': first_item.get('Status', first_item.get('status', 'Unknown')),
            'ItemCount': len(order_items),
            'OrderTotal': order_total
        })

    summary_df = pd.DataFrame(order_summaries)

    # Show summary metrics
    st.markdown("### 📊 Order Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"<div style='background:#667eea; color:white; padding:1rem; border-radius:10px; text-align:center;'><h3>{unique_orders}</h3><p>Total Orders</p></div>", unsafe_allow_html=True)
    with col2:
        if 'Status' in summary_df.columns:
            active_orders = len(summary_df[summary_df['Status'].str.lower().isin(['pending', 'processing'])])
            st.markdown(f"<div style='background:#764ba2; color:white; padding:1rem; border-radius:10px; text-align:center;'><h3>{active_orders}</h3><p>Active Orders</p></div>", unsafe_allow_html=True)
    with col3:
        if 'OrderTotal' in summary_df.columns:
            total_spent = summary_df['OrderTotal'].sum()
            st.markdown(f"<div style='background:#28a745; color:white; padding:1rem; border-radius:10px; text-align:center;'><h3>${total_spent:,.2f}</h3><p>Total Spent</p></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div style='background:#1f77b4; color:white; padding:1rem; border-radius:10px; text-align:center;'><h3>{total_items}</h3><p>Total Items</p></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_options = ['All'] + sorted(summary_df['Status'].dropna().unique().tolist()) if 'Status' in summary_df.columns else ['All']
        selected_status = st.selectbox("Filter by Status", status_options)

    with col2:
        valid_dates = summary_df['OrderDate'].dropna() if 'OrderDate' in summary_df.columns else pd.Series([])
        date_range = None
        if not valid_dates.empty:
            date_range = st.date_input("Date Range", value=(), min_value=valid_dates.min().date(), max_value=valid_dates.max().date())
        else:
            date_range = None
    with col3:
        search_term = st.text_input("🔍 Search Order ID", placeholder="Enter order ID...")

    filtered_summary = summary_df.copy()

    if selected_status != 'All':
        filtered_summary = filtered_summary[filtered_summary['Status'] == selected_status]

    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_summary = filtered_summary[
            (filtered_summary['OrderDate'].dt.date >= start_date) & 
            (filtered_summary['OrderDate'].dt.date <= end_date)
        ]

    if search_term:
        filtered_summary = filtered_summary[filtered_summary['OrderID'].astype(str).str.contains(search_term, case=False, na=False)]

    st.markdown("---")
    st.markdown(f"### 📋 Your Orders ({len(filtered_summary)} found)")

    if filtered_summary.empty:
        st.info("No orders match your current filters.")
        return

    if 'OrderDate' in filtered_summary.columns:
        filtered_summary = filtered_summary.sort_values('OrderDate', ascending=False)

    for _, order_summary in filtered_summary.iterrows():
        order_id = order_summary['OrderID']
        order_items = orders_grouped.get_group(order_id)

        order_date = order_summary['OrderDate']
        status = order_summary['Status']
        item_count = order_summary['ItemCount']
        order_total = order_summary['OrderTotal']

        formatted_date = order_date.strftime("%B %d, %Y") if pd.notna(order_date) else str(order_date)
        status_class = f"status-{status.lower().replace(' ', '-')}"

        st.markdown(f"""
        <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid #1f77b4; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem; border-bottom:1px solid #eee;">
                <div style="font-weight:bold; font-size:1.2rem; color:#1f77b4;">Order #{order_id}</div>
                <div style="padding:0.3rem 0.8rem; border-radius: 20px; font-size:0.9rem; font-weight:600; background-color:#cce5ff; color:#004085;">{status}</div>
            </div>
            <div style="background:#f8f9fa; padding:0.8rem; border-radius:8px; margin-bottom:0.5rem;">
                <strong>📅 Date:</strong> {formatted_date} &nbsp;&nbsp;
                <strong>📦 Items:</strong> {item_count} &nbsp;&nbsp;
                <strong>💰 Total:</strong> ${order_total:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"📋 View Items in Order #{order_id}"):
            product_names = order_items.get('ProductName') if 'ProductName' in order_items.columns else order_items.get('product_name', [])
            
            # Display product list
            for name in product_names:
                st.markdown(f"- **{name}**")

            st.markdown(f"**💰 Total Order Amount: ${order_total:,.2f}**")
            
            # Add recommendations section
            st.markdown("---")
            
            # Get recommendations button
            if st.button(f"✨ Get Recommendations", key=f"rec_{order_id}"):
                product_names_list = product_names.tolist() if hasattr(product_names, 'tolist') else list(product_names)
                
                if product_names_list:
                    with st.spinner("Getting recommendations..."):
                        recommendations = get_recommendations(customer_id, product_names_list)
                    
                    if recommendations:
                        st.markdown("### 🎯 Customers who bought these items also bought:")
                        for i, rec in enumerate(recommendations, 1):
                            st.markdown(f"**{i}.** {rec}")
                    else:
                        st.info("No recommendations available at this time.")
                else:
                    st.warning("No product names found in this order.")
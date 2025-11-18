"""
Electricity Bill Management System - Streamlit Web App
Single-file app (UI + SQLite backend)
Save as: electricity_bill_app.py
Author: Hemang Dhond
"""

import streamlit as st
import sqlite3
import pandas as pd
import datetime
import random
import json
import os
from io import BytesIO

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Electricity Bill System ⚡", page_icon="⚡", layout="centered")
DB_PATH = "electricity_bills.db"

# Simple user credentials (change / extend as required)
USERS = {
    "admin": "1234",   # admin user
    "user1": "1111"    # example user
}

# -----------------------------
# DATABASE (SQLite) HELPERS
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create table if not exists"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_no TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        customer_type TEXT NOT NULL,
        units REAL,
        energy_charge REAL,
        fixed_charge REAL,
        gst REAL,
        total REAL,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_bill_to_db(bill):
    """
    bill: dict with keys matching table columns
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bills
        (bill_no, customer_name, customer_type, units, energy_charge, fixed_charge, gst, total, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bill["bill_no"],
        bill["customer_name"],
        bill["customer_type"],
        bill["units"],
        bill["energy_charge"],
        bill["fixed_charge"],
        bill["gst"],
        bill["total"],
        bill["created_at"]
    ))
    conn.commit()
    conn.close()

def fetch_bills(date_from=None, date_to=None, customer_type=None):
    conn = get_db_connection()
    cur = conn.cursor()
    q = "SELECT * FROM bills WHERE 1=1"
    params = []
    if customer_type and customer_type != "All":
        q += " AND customer_type = ?"
        params.append(customer_type)
    if date_from:
        q += " AND date(created_at) >= date(?)"
        params.append(date_from)
    if date_to:
        q += " AND date(created_at) <= date(?)"
        params.append(date_to)
    q += " ORDER BY created_at DESC"
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    # convert to DataFrame
    df = pd.DataFrame([dict(r) for r in rows])
    return df

# Initialize database
init_db()

# -----------------------------
# BILL CALCULATION (Rates / Slabs)
# -----------------------------
def calculate_bill(units, customer_type):
    """
    Slab rates (example). Modify as needed.
    Domestic:
      0-100: 1.5
      101-200: 2.5
      201-500: 4.0
      >500: 6.0
    Commercial:
      0-100: 3.5
      101-200: 5.0
      201-500: 6.5
      >500: 7.5
    Fixed charges: Domestic 50, Commercial 100
    GST: 18% on energy charge
    """
    units = float(units) if units else 0.0
    if customer_type.lower() == "domestic":
        if units <= 100:
            energy = float(units) * 1.5
        elif units <= 200:
            energy = 100 * 1.5 + (float(units) - 100) * 2.5
        elif units <= 500:
            energy = 100 * 1.5 + 100 * 2.5 + (float(units) - 200) * 4.0
        else:
            energy = 100 * 1.5 + 100 * 2.5 + 300 * 4.0 + (float(units) - 500) * 6.0
        fixed = 50
    else:  # commercial
        if units <= 100:
            energy = float(units) * 3.5
        elif units <= 200:
            energy = 100 * 3.5 + (float(units) - 100) * 5.0
        elif units <= 500:
            energy = 100 * 3.5 + 100 * 5.0 + (float(units) - 200) * 6.5
        else:
            energy = 100 * 3.5 + 100 * 5.0 + 300 * 6.5 + (float(units) - 500) * 7.5
        fixed = 100

    gst = energy * 0.18
    total = energy + fixed + gst
    # Round values
    return round(energy,2), round(fixed,2), round(gst,2), round(total,2)

# -----------------------------
# AUTHENTICATION
# -----------------------------
def login(username, password):
    return username in USERS and USERS[username] == password

# -----------------------------
# UI PAGES
# -----------------------------
def login_page():
    st.title("⚡ Electricity Bill Management System")
    st.subheader("🔐 Login")
    with st.form("login_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        username = col1.text_input("Username")
        password = col2.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    if submitted:
        if login(username, password):
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials. (default admin/1234)")

def generate_bill_page():
    st.title("🧾 Generate Electricity Bill")
    st.markdown("Enter customer details and units consumed, then click **Generate Bill**.")

    col1, col2 = st.columns([2,2])
    with col1:
        customer_name = st.text_input("Customer Name")
        customer_type = st.selectbox("Customer Type", ["Domestic","Commercial"])
    with col2:
        units = st.number_input("Units Consumed", min_value=0.0, format="%.2f", step=1.0)
        generate = st.button("Generate Bill")

    if generate:
        if not customer_name:
            st.warning("Please enter customer name.")
        else:
            energy_charge, fixed_charge, gst, total = calculate_bill(units, customer_type)
            bill_no = f"BILL{random.randint(10000,99999)}"
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Show bill nicely
            st.markdown("---")
            st.markdown(f"### ⚡ Bill — {bill_no}")
            st.write(f"**Customer:** {customer_name}")
            st.write(f"**Customer Type:** {customer_type}")
            st.write(f"**Date:** {date_str}")
            st.write(f"**Units:** {units}")
            st.markdown("---")
            st.write(f"**Energy Charge:** ₹ {energy_charge:.2f}")
            st.write(f"**Fixed Charge:** ₹ {fixed_charge:.2f}")
            st.write(f"**GST (18%):** ₹ {gst:.2f}")
            st.markdown(f"### 💰 Total Payable: ₹ {total:.2f}")
            st.markdown("---")

            # Save bill to DB
            bill = {
                "bill_no": bill_no,
                "customer_name": customer_name,
                "customer_type": customer_type,
                "units": units,
                "energy_charge": energy_charge,
                "fixed_charge": fixed_charge,
                "gst": gst,
                "total": total,
                "created_at": date_str
            }
            save_bill_to_db(bill)
            st.success("Bill saved to database ✅")

            # Download single bill as CSV
            df_one = pd.DataFrame([bill])
            csv_bytes = df_one.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Bill (CSV)", data=csv_bytes, file_name=f"{bill_no}.csv", mime="text/csv")

def reports_page():
    st.title("📊 Bills & Reports")
    col1, col2, col3 = st.columns(3)
    with col1:
        customer_type = st.selectbox("Customer Type", ["All","Domestic","Commercial"])
    with col2:
        date_from = st.date_input("From", value=datetime.date.today().replace(day=1))
    with col3:
        date_to = st.date_input("To", value=datetime.date.today())

    df = fetch_bills(date_from=date_from.strftime("%Y-%m-%d"), date_to=date_to.strftime("%Y-%m-%d"), customer_type=customer_type)
    if df.empty:
        st.info("No bills found for the selected filter.")
    else:
        # Format df for display
        df_display = df.copy()
        df_display["created_at"] = pd.to_datetime(df_display["created_at"])
        st.dataframe(df_display[["bill_no","customer_name","customer_type","units","energy_charge","fixed_charge","gst","total","created_at"]].rename(columns={
            "bill_no":"Bill No","customer_name":"Customer","customer_type":"Type","units":"Units","energy_charge":"Energy","fixed_charge":"Fixed","gst":"GST","total":"Total","created_at":"Date"
        }), use_container_width=True)

        # Metrics
        total_revenue = df["total"].sum()
        total_bills = len(df)
        st.metric("Total Bills", total_bills)
        st.metric("Total Revenue (₹)", f"{total_revenue:.2f}")

        # Download report CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Report (CSV)", data=csv, file_name=f"bills_{date_from}_{date_to}.csv", mime="text/csv")

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# -----------------------------
# MAIN APP LAYOUT
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title("⚙️ Menu")
    st.sidebar.write(f"👋 Logged in as **{st.session_state.user}**")
    choice = st.sidebar.radio("Navigation", ["Generate Bill","Bills & Reports","Logout"])
    st.sidebar.markdown("---")
    st.sidebar.markdown("Project: Electricity Bill System")

    if choice == "Generate Bill":
        generate_bill_page()
    elif choice == "Bills & Reports":
        reports_page()
    elif choice == "Logout":
        logout()

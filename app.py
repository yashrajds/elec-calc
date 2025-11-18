# app.py
import streamlit as st
import pandas as pd
import datetime
import webbrowser
import threading
import time
import os
from database import init_db, get_user, create_user, save_bill, fetch_bills, backup_db_bytes, restore_db_bytes, update_bill_status
from backend import hash_password, verify_password, make_bill
from utils import generate_bill_pdf_bytes

def open_browser():
    time.sleep(3)  # Wait for Streamlit server to start
    webbrowser.open("http://localhost:8501")

# Prevent multiple browser openings
if not os.path.exists('.browser_opened'):
    with open('.browser_opened', 'w') as f:
        f.write('opened')
    threading.Thread(target=open_browser).start()

# Setup
st.set_page_config(page_title="Electricity Bill System ⚡", page_icon="⚡", layout="wide")
init_db()

# Ensure default admin exists (create with hashed password if missing)
if get_user("admin") is None:
    create_user("admin", hash_password("1234"), role="admin")

# session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

# ---- Authentication UI ----
def login_ui():
    st.title("⚡ Electricity Bill Management System")
    st.write("**Login**")
    with st.form("login_form"):
        col1, col2 = st.columns([2,2])
        username = col1.text_input("Username")
        password = col2.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    if submitted:
        user = get_user(username)
        if user and verify_password(password, user["password_hash"]):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def register_ui():
    st.title("Register new user")
    with st.form("register_form"):
        u1, u2, u3 = st.columns([2,2,1])
        username = u1.text_input("Username")
        password = u2.text_input("Password", type="password")
        role = u3.selectbox("Role", ["user","admin"])
        submit = st.form_submit_button("Register")
    if submit:
        if get_user(username):
            st.warning("Username already exists.")
        else:
            create_user(username, hash_password(password), role=role)
            st.success("User created. Ask admin to login.")

# ---- Main App Pages ----
def generate_bill_page():
    st.header("🧾 Generate Electricity Bill")
    with st.form("gen"):
        c1, c2 = st.columns([2,1])
        with c1:
            customer_name = st.text_input("Customer Name")
            customer_type = st.selectbox("Customer Type", ["Domestic","Commercial"])
        with c2:
            units = st.number_input("Units Consumed (kWh)", min_value=0.0, value=0.0, step=1.0)
            paid_flag = st.selectbox("Status", ["Unpaid","Paid"])
            generate = st.form_submit_button("Generate & Save")
    if generate:
        if not customer_name:
            st.warning("Enter customer name.")
            return
        bill = make_bill(customer_name, customer_type, units, status=paid_flag)
        if isinstance(bill, dict) and "error" in bill:
            st.error("We cannot process this bill amount. Please recheck your unit entry.")
            return
        save_bill(bill)
        st.success("Bill generated and saved.")
        st.markdown("### Bill Preview")
        st.metric("Total (₹)", f"{bill['total']:.2f}")
        st.write(bill)
        # downloads
        pdf_bytes = generate_bill_pdf_bytes(bill)
        st.download_button("⬇️ Download PDF", data=pdf_bytes, file_name=f"{bill['bill_no']}.pdf", mime="application/pdf")
        st.download_button("⬇️ Download CSV", data=pd.DataFrame([bill]).to_csv(index=False).encode(), file_name=f"{bill['bill_no']}.csv")

def reports_page():
    st.header("📊 Reports & Analytics")
    c1, c2, c3, c4 = st.columns([1.5,1.5,1,1])
    with c1:
        cust_type = st.selectbox("Customer Type", ["All","Domestic","Commercial"])
    with c2:
        date_from = st.date_input("From", value=datetime.date.today().replace(day=1))
    with c3:
        date_to = st.date_input("To", value=datetime.date.today())
    with c4:
        status = st.selectbox("Status", ["All","Unpaid","Paid"])

    df = fetch_bills(date_from=date_from.strftime("%Y-%m-%d"), date_to=date_to.strftime("%Y-%m-%d"), customer_type=cust_type, status=status)
    if df.empty:
        st.info("No bills found for selected filters.")
        return

    df["created_at"] = pd.to_datetime(df["created_at"])
    st.dataframe(df[['bill_no','customer_name','customer_type','units','energy_charge','fixed_charge','gst','total','status','created_at']].rename(columns={
        'bill_no':'Bill No','customer_name':'Customer','customer_type':'Type','units':'Units','energy_charge':'Energy','fixed_charge':'Fixed','gst':'GST','total':'Total','created_at':'Date'
    }), use_container_width=True)

    total_revenue = df['total'].sum()
    total_bills = len(df)
    avg_units = df['units'].mean()

    st.metric("Total Bills", total_bills)
    st.metric("Total Revenue (₹)", f"{total_revenue:.2f}")
    st.metric("Average Units", f"{avg_units:.2f}")

    # simple charts
    st.subheader("Revenue by Type")
    by_type = df.groupby('customer_type')['total'].sum().reset_index()
    st.bar_chart(by_type.set_index('customer_type'))

    st.subheader("Daily Revenue")
    daily = df.groupby(df['created_at'].dt.date)['total'].sum()
    st.line_chart(daily)

    # Export
    st.download_button("⬇️ Download Report (CSV)", data=df.to_csv(index=False).encode(), file_name=f"report_{date_from}_{date_to}.csv", mime="text/csv")

    # quick status update (admin only)
    if st.session_state.role == "admin":
        st.markdown("---")
        st.subheader("Admin Tools — Update Bill Status")
        sel = st.selectbox("Select Bill No", df['bill_no'].tolist())
        new_status = st.selectbox("Set Status To", ["Paid","Unpaid"])
        if st.button("Update Status"):
            update_bill_status(sel, new_status)
            st.success("Status updated. Refresh to see changes.")

def admin_panel():
    st.header("🛠️ Admin Panel")
    st.subheader("Create new user")
    with st.form("admin_create_user"):
        u1, u2, u3 = st.columns([2,2,1])
        username = u1.text_input("Username")
        password = u2.text_input("Password", type="password")
        role = u3.selectbox("Role", ["user","admin"])
        submit = st.form_submit_button("Create User")
    if submit:
        if get_user(username):
            st.warning("User already exists.")
        else:
            create_user(username, hash_password(password), role)
            st.success("User created.")

    st.markdown("---")
    st.subheader("Database Backup / Restore")
    if st.button("🔽 Download DB Backup"):
        b = backup_db_bytes()
        st.download_button("Download DB", data=b, file_name="electricity_bills_backup.db", mime="application/octet-stream")
    uploaded = st.file_uploader("Restore DB (upload .db file)", type=["db"])
    if uploaded:
        restore_db_bytes(uploaded.read())
        st.success("Database restored; please refresh the app.")
        st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

# ---- App layout ----
if not st.session_state.logged_in:
    col1, col2 = st.columns(2)
    with col1:
        login_ui()
    with col2:
        st.info("New user? Register here.")
        register_ui()
else:
    st.sidebar.title("⚙️ Menu")
    st.sidebar.write(f"👋 Logged in as **{st.session_state.username}** ({st.session_state.role})")
    if st.session_state.role == "admin":
        choice = st.sidebar.radio("Navigation", ["Generate Bill","Reports","Admin","Logout"])
    else:
        choice = st.sidebar.radio("Navigation", ["Generate Bill","Reports","Logout"])

    if choice == "Generate Bill":
        generate_bill_page()
    elif choice == "Reports":
        reports_page()
    elif choice == "Admin":
        admin_panel()
    elif choice == "Logout":
        logout()

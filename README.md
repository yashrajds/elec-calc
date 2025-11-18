
# Electricity Bill Management System

[![Streamlit](https://img.shields.io/badge/built_with-Streamlit-blue)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## 🚀 Project Overview

The **Electricity Bill Management System** is a complete web application built with Streamlit to generate, manage, and report electricity bills for different customer types (Domestic and Commercial). This application supports user authentication, dynamic bill calculations based on slab rates, PDF and CSV bill generation, and administrative control features like user management and database backup.

---

## ✨ Features

- User Authentication with roles (admin and user)
- Generate electricity bills with dynamic rate slabs
- Store bills in SQLite database
- Download bills in PDF and CSV formats
- View and filter billing reports with date and customer type
- Admin panel for user management and database backups/restoration
- Streamlit-based interactive and user-friendly interface

---

## 🛠️ Technologies Used

- Python 3.8+
- Streamlit (1.20.0)
- SQLite for database management
- Pandas for data handling
- ReportLab & Pillow for PDF generation
- Hashlib for secure password hashing

---

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/electricity-bill-system.git
   cd electricity-bill-system
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scriptsctivate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚡ Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

- Open your web browser to `http://localhost:8501`
- Login with default admin credentials:
  - Username: `admin`
  - Password: `1234`
- Navigate through the sidebar menu:
  - Generate and save electricity bills
  - View detailed reports and analytics
  - Admin panel for managing users and database

---

## 🧩 Code Structure

| Filename               | Description                                     |
|------------------------|-------------------------------------------------|
| `app.py`               | Main Streamlit app UI and routing                |
| `electricity_bill_app.py` | Alternative or earlier Streamlit app version       |
| `backend.py`           | Business logic: password hashing, billing logic |
| `database.py`          | Database operations and connection               |
| `utils.py`             | PDF generation utilities                          |
| `requirements.txt`     | Project dependencies                              |

---

## 🧑‍💻 How It Works

1. **User Authentication:** Secure login with hashed passwords.
2. **Bill Generation:** Input customer details & units, auto-calculates charges.
3. **Bill Storage:** Saves bill info into SQLite DB.
4. **Reports:** Interactive filtering on date, type, and status; metrics & charts.
5. **Admin Options:** Create users, backup, and restore database.

---

## 🛡️ Security

- Passwords are hashed using SHA-256.
- Role-based access control (Admin/User).
- Input validation for units to prevent invalid bill entries.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Author

**Hemang Dhond**

---

## 📥 Download README

You can copy this README content or download it from the project repository if hosted on GitHub.

---

Thank you for using the Electricity Bill Management System! Please report issues or contribute via pull requests.

---

*Happy Billing! ⚡*

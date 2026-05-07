# 🧾 Django ERP Billing System

A scalable ERP-style billing and inventory management system built using Django.  
This project includes real-world business features such as invoice generation, stock tracking, role-based access control, and dashboard analytics.

---

## 🚀 Features

### 🔐 Authentication & Roles
- Custom user model
- Role-based login (Admin, Staff, Accountant)
- Access control per module

### 📦 Product Management
- Add, edit, delete products
- Category support
- SKU-based tracking
- Stock management with low stock alerts

### 👥 Customer Management
- Add and manage customers
- Pagination support

### 🧾 Invoice System
- Create invoices with multiple items
- Auto price calculation
- GST calculation
- Grand total computation
- Stock reduction on invoice creation

### 📊 Dashboard
- Total revenue
- Total invoices
- Product count
- Low stock alerts
- Sales chart (Chart.js)
- Recent invoices
- Top selling products

---

## 🛠️ Tech Stack

- Python
- Django
- SQLite (can be switched to PostgreSQL/MySQL)
- Bootstrap (UI)
- Chart.js (analytics)

---

## 📁 Project Structure
accounts/ # authentication and roles
products/ # product & inventory management
customers/ # customer data
invoices/ # billing system
templates/ # UI templates



---

## ⚙️ Installation


git clone https://github.com/subinpk8088-pydj/django-erp-billing-system.git
cd billing-system

python -m venv env
env\Scripts\activate   # Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

🔑 Default Roles
Admin → Full access
Staff → Invoice operations
Accountant → Reports and financial data
⚠️ Current Limitations
No payment gateway integration
No multi-branch support
Limited reporting filters
No audit logs (planned)
🚀 Future Improvements
Advanced reporting (monthly/yearly)
Profit calculation
Export to PDF/Excel
Role-based dashboards
Activity logs
👨‍💻 Author

Subin PK

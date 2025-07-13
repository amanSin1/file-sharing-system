# 🔐 Secure File Sharing System (Django REST API)

This project is a **secure file-sharing system** built with Django and Django REST Framework, designed for two types of users: **Ops** and **Client**. It supports file upload, secure downloads via encrypted URLs, and email verification.

---

## 🚀 Features

- ✅ User Registration with Email Verification
- 🔐 JWT Authentication
- 🗃️ File Upload (with file type metadata)
- 📥 Secure Download URL generation (only for clients)
- ✉️ Email-based verification  // Django console backend for email verification in development.
- 📁 File visibility only after verification

---

## 👤 User Roles

1. **Ops User**
   - Can sign up and log in
   - Upload files

2. **Client User**
   - Can sign up and log in
   - Must verify email before accessing files
   - Can list all available files
   - Can request a secure download URL

---

## 📦 Tech Stack

- Python 3.11+
- Django 4.x
- Django REST Framework
- djangorestframework-simplejwt (JWT Authentication)
- PostgreSQL / SQLite (for dev)
- Python `cryptography` module (for secure URL encryption)
- Postman (for API testing)

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/signup/` | User registration (client or ops) |
| `POST` | `/api/login/` | Login and get JWT tokens |
| `GET`  | `/api/verify-email/<token>/` | Verify email |
| `POST` | `/api/upload/` | (Ops only) Upload a file |
| `GET`  | `/api/files/` | (Client only) List all uploaded files |
| `GET`  | `/api/files/<file_id>/download-url/` | Get secure download URL |
| `GET`  | `/api/download/<encrypted_url>/` | Download the actual file |

---

## 📂 Postman Collection

You can find the full Postman Collection here:  
📄 [`file-sharing_postman_collection.json`](./file-sharing_postman_collection.json)


To use it:
1. Open Postman
2. Go to "Import" → "File"
3. Select the JSON file
4. Test all APIs easily

---

## 🛠️ Running the Project Locally

```bash
git clone https://github.com/yourusername/file-sharing-system.git
cd file-sharing-system
python -m venv venv
source venv/bin/activate  # on Windows use `venv\Scripts\activate`
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Research Grant Management System (RGMS)

A Django-based web application for managing research grants, applications, and approvals within an academic institution.

## Features

- **User Management** - Custom user model with role-based access (Faculty, HOD, Admin)
- **Grant Applications** - Submit and track research grant applications
- **Approval Workflows** - Multi-level approval process for grant requests
- **Analytics Dashboard** - Department-level analytics and reporting
- **PDF Export** - Export analytics reports as PDF documents
- **Admin Panel** - Comprehensive administrative interface

## Quick Start

### 1. Clone the Repository

```bash
git clone <https://github.com/MrMinton/Research-Grant-Management-System.git>
cd Research-Grant-Management-System
```

### 2. Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
cd rgms_config
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

### 7. Access the Application

Open your browser and navigate to:
- **Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Tech Stack

- **Backend**: Django 6.0
- **Database**: SQLite3
- **PDF Generation**: xhtml2pdf
- **Frontend**: HTML, CSS, JavaScript

## Project Structure

```
rgms_config/
├── grants/          # Grant management app
├── users/           # User management app
├── static/          # Static files (CSS, JS)
├── templates/       # HTML templates
├── media/           # Uploaded files
└── rgms_config/     # Project configuration
```

## Requirements

- Python 3.8+
- pip
- See [requirements.txt](requirements.txt) for Python package dependencies

## Contributors

- Suraj Prakash
- Law Jun Feng
- Lim Jian Feng

# Installation / Setup Guide

## Research Grant Management System (RGMS)

This guide will walk you through setting up the Research Grant Management System on your local development environment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Database Setup](#database-setup)
4. [Static Files Configuration](#static-files-configuration)
5. [Running the Application](#running-the-application)
6. [Creating a Superuser](#creating-a-superuser)
7. [Troubleshooting](#troubleshooting)
8. [Additional Configuration](#additional-configuration)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (comes with Python)
- **Git** - [Download Git](https://git-scm.com/downloads) (optional, for cloning)

---

## Installation Steps

### 1. Clone or Download the Repository

```bash
# If using Git
git clone <https://github.com/MrMinton/Research-Grant-Management-System.git>
cd Research-Grant-Management-System

# Or download and extract the ZIP file, then navigate to the directory
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

#### Dependencies Installed:
- `Django==6.0` - Web framework
- `asgiref==3.11.0` - ASGI specs, Django dependency
- `sqlparse==0.5.5` - SQL parsing library
- `tzdata==2025.3` - Timezone data
- `xhtml2pdf` - PDF generation library

---

## Database Setup

The application uses SQLite3 as the default database (no additional installation required).

### 1. Navigate to the Project Directory

```bash
cd rgms_config
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create the database file `db.sqlite3` and set up all necessary tables.

---

## Static Files Configuration

The application uses static files (CSS, JavaScript) located in the `static` directory.

### Collect Static Files (Production Only)

For production deployments, run:

```bash
python manage.py collectstatic
```

For development, Django automatically serves static files from the `STATICFILES_DIRS`.

---

## Running the Application

### 1. Start the Development Server

From the `rgms_config` directory:

```bash
python manage.py runserver
```

### 2. Access the Application

Open your web browser and navigate to:

```
http://127.0.0.1:8000/
```

or

```
http://localhost:8000/
```

---

## Creating a Superuser

To access the Django admin panel and manage the application:

```bash
python manage.py createsuperuser
```

You'll be prompted to enter:
- Username
- Email address
- Password (enter twice for confirmation)

### Access Admin Panel

After creating the superuser, visit:

```
http://127.0.0.1:8000/admin/
```

Log in with your superuser credentials.

---

## Troubleshooting

### Common Issues and Solutions

#### 1. **Port Already in Use**

If port 8000 is already occupied, you can specify a different port:

```bash
python manage.py runserver 8080
```

#### 2. **Module Not Found Error**

Ensure your virtual environment is activated and all dependencies are installed:

```bash
pip install -r requirements.txt
```

#### 3. **Migration Errors**

If you encounter migration issues, try:

```bash
python manage.py migrate --run-syncdb
```

#### 4. **Static Files Not Loading**

Ensure `DEBUG = True` in `settings.py` for development. Check that `STATICFILES_DIRS` is properly configured.

#### 5. **PDF Export Not Working**

The `xhtml2pdf` library requires proper dependencies. If issues occur, try reinstalling:

```bash
pip uninstall xhtml2pdf
pip install xhtml2pdf
```

---

## Additional Configuration

### Security Settings (Production)

> [!WARNING]
> Before deploying to production, update the following in `rgms_config/settings.py`:

1. **SECRET_KEY**: Generate a new secret key
   ```python
   SECRET_KEY = 'your-new-secret-key-here'
   ```

2. **DEBUG**: Set to False
   ```python
   DEBUG = False
   ```

3. **ALLOWED_HOSTS**: Add your domain
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

### Media Files

The application stores uploaded files in the `media` directory. Ensure this directory exists and has proper permissions:

```bash
# This directory should already exist, but if not:
mkdir media
```

### Custom User Model

This application uses a custom user model (`users.User`). All user-related operations should reference this model.

---

## Application Structure

```
Research-Grant-Management-System/
├── rgms_config/              # Main Django project
│   ├── grants/               # Grants application
│   ├── users/                # Users application
│   ├── static/               # Static files (CSS, JS, images)
│   ├── templates/            # HTML templates
│   ├── media/                # User-uploaded files
│   ├── rgms_config/          # Project settings
│   │   ├── settings.py       # Django settings
│   │   ├── urls.py           # URL routing
│   │   └── wsgi.py           # WSGI configuration
│   ├── manage.py             # Django management script
│   └── db.sqlite3            # SQLite database (created after migrations)
├── venv/                     # Virtual environment
├── requirements.txt          # Python dependencies
└── .gitignore                # Git ignore rules
```

---

## Next Steps

1. **Explore the Admin Panel**: Log in to `/admin/` to manage users and grants
2. **Create Test Data**: Add sample grants and users to test functionality
3. **Review Features**: Test the grant application, approval workflows, and analytics
4. **Export Analytics**: Try the PDF export feature for department analytics

---

## Support

For issues or questions:
- Check the Django documentation: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- Review the application code in the respective app directories (`users/`, `grants/`)

---

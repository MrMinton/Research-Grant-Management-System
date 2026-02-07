Research Grant Management System (RGMS)
A web-based application built with Django to facilitate the management of research grants, proposal submissions, evaluations, and budget tracking. The system supports multiple user roles including Researchers, Reviewers, and Heads of Department (HOD).

Features
User Roles & Management
Researchers: Can submit grant proposals, track status, and submit progress reports with expenditure details.

Reviewers: Responsible for evaluating proposals by providing scores and feedback comments.

Heads of Department (HOD): Oversee department budgets and grant allocations.

Core Functionality
Proposal Management: * Submission of proposals with title, requested amount, and file uploads (PDF/DOC/DOCX support).

Version tracking and status updates (e.g., Draft, Submitted).

Grant Administration: * Tracks total allocated amounts, start dates, and end dates.

Visual usage percentage tracking for quick budget analysis.

Budget & Financials:

Tracks total spent vs. allocated amounts.

Automatic calculation of remaining balances.

Progress Reporting: * Researchers can submit reports detailing milestones achieved and specific expenditures for the reporting period.

Notifications: * Built-in notification system to alert users of important updates.

Tech Stack
Framework: Django 6.0

Database: SQLite (Default)

Language: Python

Utilities: xhtml2pdf for PDF generation
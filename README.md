# Weblancer Project

**Weblancer** is a freelance job marketplace built using **Django**, where clients can post projects and freelancers can submit proposals, bid on projects, and communicate through a secure system. It includes bidding logic, proposal management, authentication, and a clear workflow between clients and freelancers.

---

## 🔧 Features

- User roles: **Client** and **Freelancer**
- Clients can:
  - Post projects with budgets and descriptions
  - View all proposals for their posted projects
  - Accept or reject freelancer proposals
- Freelancers can:
  - View open projects
  - Submit proposals with bid price and cover letter
  - View and update their own proposals
- Proposal status management (Pending, Accepted, Rejected)
- Secure access control
- Real-time updates with modals and AJAX (Accept Proposal Modal)
- Fully functional authentication system (Login, Logout, Registration)

---

## 🚀 Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript (AJAX for dynamic actions)
- **Database**: SQLite (can be changed to PostgreSQL or MySQL)
- **Authentication**: Django built-in auth system
- **Other tools**: CSRF protection, Django messages framework

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

The static/ directory contains a compressed file named bootstrap-icons.zip.
Before running the project, make sure to extract this ZIP file so that the Bootstrap icons can load correctly in the UI.

```bash
git clone https://github.com/ssankapelli/weblancer-project.git
cd weblancer-project

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
```Folder Structure (Key Files)

weblancer-project/
│
├── static/                      # Static files (CSS, JS)
├── users/                       # User accounts and authentication
├── projects/                    # Project posting and detail views
├── proposals/                   # Bidding and proposal logic
├── reviews/                   
│
├── manage.py
└── README.md                    # You're here!
```

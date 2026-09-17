# Student Management System

A full-stack CRUD web application that manages student records for a college
department. Built with a Django REST Framework backend, an SQLite database, and
an HTML/CSS/JavaScript frontend that talks to the API using `fetch`.

```
Browser (HTML/CSS/JS)  →  REST API  →  Django REST Framework  →  ORM  →  SQLite
```

## What it does

| Operation | How to use it | What happens |
|---|---|---|
| Create | Fill the form, press **Save student** | Record is validated, stored, and appears in the table |
| Read | Open the page | All records load; search and department filter narrow the list |
| Update | Press **Edit** on a row, change values, press **Update student** | Record is updated in place |
| Delete | Press **Delete** on a row, confirm | Record is removed from the database and the table |

## Project structure

```
student-management/
├── backend/
│   ├── config/              Django project settings and root URLs
│   ├── students/            The app: model, serializer, views, URLs, tests
│   │   ├── models.py        Student entity and database constraints
│   │   ├── serializers.py   Server-side validation
│   │   ├── views.py         CRUD endpoints, search, stats
│   │   ├── exceptions.py    Uniform error responses
│   │   ├── tests.py         17 automated tests
│   │   └── fixtures/        Sample data for the demo
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js               fetch calls, client-side validation
├── docs/
│   ├── API.md               Endpoint documentation
│   ├── REPORT.md            Project report template
│   └── postman_collection.json
└── .gitignore
```

## Setup

You need Python 3.10 or newer.

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata sample_students    # optional: 5 demo records
python manage.py runserver
```

The API is now at `http://127.0.0.1:8000/api/students/`.

### 2. Frontend

Open a second terminal:

```bash
cd frontend
python -m http.server 5500
```

Then visit `http://127.0.0.1:5500` in your browser.

> Serve the frontend over `http://` rather than opening `index.html` by
> double-clicking it. Browsers block API calls from `file://` pages.

### 3. Admin panel (optional)

```bash
cd backend
python manage.py createsuperuser
```

Then visit `http://127.0.0.1:8000/admin/` to inspect the database directly.

## Running the tests

```bash
cd backend
python manage.py test
```

All 17 tests should pass. They cover create with valid, missing, duplicate and
invalid data; read on empty and populated databases; update and delete with
valid and invalid IDs; and the search filter.

## Configuration

Secrets are read from environment variables, never hard-coded. Copy
`backend/.env.example` to `backend/.env` and set real values before deploying.
The project runs out of the box in development without any of them.

## Switching to MySQL or PostgreSQL

Edit `DATABASES` in `backend/config/settings.py`, install the matching driver
(`mysqlclient` or `psycopg2-binary`), then run `python manage.py migrate` again.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot reach the API" in the browser | The Django server isn't running. Start it on port 8000. |
| CORS error in the browser console | Serve the frontend over `http://`, not `file://`. |
| `ModuleNotFoundError: No module named 'rest_framework'` | The virtual environment isn't active, or `pip install -r requirements.txt` didn't run. |
| Port 8000 already in use | `python manage.py runserver 8001` and update `API_ROOT` in `frontend/app.js`. |

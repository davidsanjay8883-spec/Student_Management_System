# Student Management System — Project Report

> Fill in the bracketed parts and paste your screenshots where marked. The
> sections follow section 13 of the SOP in order.

**Student name:** [your name]
**Roll number:** [your roll number]
**Course / subject:** [course code and name]
**Submission date:** [date]

---

## 1. Project overview

A full-stack web application that lets a department maintain its student
records. The user can add a student, view the whole register, search it, edit
any record, and delete a record. All data is stored in a relational database
and reached through a REST API.

## 2. Problem statement

Student records in many departments are kept in spreadsheets that are copied
between staff members. Two people editing the same file produce conflicting
versions, there is nothing to stop a duplicate roll number being entered, and
finding one student means scrolling. A single shared application with a
database behind it removes all three problems.

## 3. Objectives

- Design a database table that holds student details with correct data types
  and constraints.
- Build a REST API exposing all four CRUD operations.
- Build a responsive interface that consumes the API.
- Validate input on both the client and the server.
- Handle errors so the user always sees a clear message.
- Test every endpoint and record the results.

## 4. Technology stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | Direct control over the interface with no build step |
| API calls | Fetch API | Built into the browser |
| Backend | Django 5 + Django REST Framework | Fast to build REST APIs; validation is built in |
| Database | SQLite | No server to install; ships with Python |
| ORM | Django ORM | Parameterised queries, so no SQL injection |
| Testing | Postman + Django test framework | Manual and automated coverage |
| Version control | Git and GitHub | Tracked history of the work |

## 5. System architecture

```
┌──────────────────────────────┐
│  Browser                     │
│  index.html / styles.css     │
│  app.js  (fetch, validation) │
└───────────────┬──────────────┘
                │ HTTP + JSON
                ▼
┌──────────────────────────────┐
│  Django REST Framework       │
│  urls.py   → routing         │
│  views.py  → CRUD logic      │
│  serializers.py → validation │
│  exceptions.py  → errors     │
└───────────────┬──────────────┘
                │ Django ORM
                ▼
┌──────────────────────────────┐
│  SQLite — students_student   │
└──────────────────────────────┘
```

The three layers are kept separate. The browser never touches the database;
the backend never produces HTML. They communicate only through JSON over HTTP,
which is why either side could be replaced (React instead of plain JavaScript,
PostgreSQL instead of SQLite) without rewriting the other.

## 6. Database design

**Table:** `students_student`

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | Primary key, auto-increment |
| `roll_number` | VARCHAR(15) | NOT NULL, UNIQUE |
| `full_name` | VARCHAR(100) | NOT NULL |
| `email` | VARCHAR(254) | NOT NULL, UNIQUE |
| `phone` | VARCHAR(10) | Nullable, 10 digits when present |
| `department` | VARCHAR(10) | NOT NULL, restricted to six codes |
| `year_of_study` | SMALLINT | NOT NULL, 1–4 |
| `cgpa` | DECIMAL(4,2) | NOT NULL, 0.00–10.00 |
| `created_at` | DATETIME | Set automatically on insert |
| `updated_at` | DATETIME | Set automatically on every save |

**ER diagram**

```
┌─────────────────────────────┐
│          STUDENT            │
├─────────────────────────────┤
│ PK  id                      │
│ UQ  roll_number             │
│     full_name               │
│ UQ  email                   │
│     phone                   │
│     department              │
│     year_of_study           │
│     cgpa                    │
│     created_at              │
│     updated_at              │
└─────────────────────────────┘
```

This version manages a single entity. Section 12 describes how a `Course`
entity would extend it into a many-to-many relationship.

> `cgpa` uses DECIMAL rather than FLOAT because floating-point numbers cannot
> represent values like 8.75 exactly, which would make averages drift.

## 7. UI screenshots

> Take these while the app is running and paste them here.

1. The register with several records loaded — *[screenshot]*
2. The add form filled in — *[screenshot]*
3. Validation errors showing under the fields — *[screenshot]*
4. A record being edited — *[screenshot]*
5. The delete confirmation — *[screenshot]*
6. The page at mobile width — *[screenshot]*

## 8. API endpoint documentation

See `docs/API.md` for the full reference. Summary:

| Operation | Method | Endpoint | Success |
|---|---|---|---|
| Create | POST | `/api/students/` | 201 |
| Read all | GET | `/api/students/` | 200 |
| Read one | GET | `/api/students/{id}/` | 200 |
| Update | PUT / PATCH | `/api/students/{id}/` | 200 |
| Delete | DELETE | `/api/students/{id}/` | 200 |

## 9. CRUD implementation details

**Create.** The form gathers the fields and `app.js` checks them before any
request is sent. It POSTs JSON to `/api/students/`. `StudentSerializer`
re-checks everything on the server, the ORM inserts the row, and the API
returns the saved object including its new `id`. The table then reloads.

**Read.** On page load `app.js` GETs `/api/students/`. Typing in the search box
re-requests with `?search=`, debounced by 250 ms so one request goes out per
pause rather than one per keystroke. The department dropdown adds
`?department=`. Filtering happens in the database, not in the browser.

**Update.** Pressing Edit fetches that single record, fills the form, and
stores the ID in a hidden field. Submitting then sends PUT to
`/api/students/{id}/` instead of POST. The same validation runs.

**Delete.** A confirmation dialog runs first. DELETE is sent to
`/api/students/{id}/`; the API returns a message naming the deleted roll
number, and the table reloads.

## 10. Validation

| Rule | Client | Server |
|---|---|---|
| Required fields not empty | ✓ | ✓ |
| Valid email format | ✓ | ✓ |
| Roll number unique | — | ✓ (database UNIQUE constraint) |
| Email unique | — | ✓ (database UNIQUE constraint) |
| Year between 1 and 4 | ✓ | ✓ |
| CGPA between 0 and 10 | ✓ | ✓ |
| Phone exactly 10 digits | ✓ | ✓ |
| Name at least 3 characters | ✓ | ✓ |

Client-side validation exists for speed — the user sees the problem without
waiting for a round trip. Server-side validation exists for correctness,
because anyone can bypass the browser and call the API directly from Postman.
Uniqueness is only checked on the server, since the browser cannot know what is
already in the database.

## 11. Testing results

### Automated tests

`python manage.py test` runs 17 tests and all pass.

> *[screenshot of the test output]*

### Postman test cases

| # | Test | Input | Expected | Actual | Result |
|---|---|---|---|---|---|
| 1 | Create with valid data | Full valid record | 201 Created | | |
| 2 | Create with missing name | `full_name` removed | 400, names `full_name` | | |
| 3 | Create with invalid email | `email: "abc"` | 400, names `email` | | |
| 4 | Create with duplicate roll number | Existing roll number | 400, names `roll_number` | | |
| 5 | Create with CGPA 12.5 | Out of range | 400, names `cgpa` | | |
| 6 | Create with year 7 | Out of range | 400, names `year_of_study` | | |
| 7 | Read all, empty database | — | 200, `[]` | | |
| 8 | Read all, populated | — | 200, array of records | | |
| 9 | Read one, valid ID | `/students/1/` | 200, one object | | |
| 10 | Read one, invalid ID | `/students/9999/` | 404 | | |
| 11 | Update, valid ID | Changed CGPA | 200, new value | | |
| 12 | Update, invalid ID | `/students/9999/` | 404 | | |
| 13 | Delete, valid ID | `/students/1/` | 200, record gone | | |
| 14 | Delete, invalid ID | `/students/9999/` | 404 | | |
| 15 | Search | `?search=anitha` | Only matches | | |
| 16 | Backend stopped | Any UI action | Clear error message shown | | |

> Fill in Actual and Result as you run each one, and attach screenshots.

### Responsiveness

Checked at desktop width and at mobile width (375 px). The two-column layout
collapses to a single column and the table scrolls horizontally rather than
overflowing the page.

## 12. Installation and execution

See the README. In short: create a virtual environment, install
`requirements.txt`, run `migrate`, start `runserver`, then serve the `frontend`
folder over HTTP and open it.

## 13. Challenges and solutions

| Challenge | Solution |
|---|---|
| Browser blocked API calls from a different port (CORS) | Added `django-cors-headers` middleware and allowed the frontend origin in development |
| DRF returned several different error shapes, so the frontend needed several parsers | Wrote a custom exception handler that wraps every error in one `{success, message, errors}` format |
| Search fired a request on every keystroke | Debounced the input by 250 ms |
| Averages of CGPA drifted slightly | Stored CGPA as DECIMAL instead of FLOAT |
| Duplicate roll numbers slipped past the form | Added a UNIQUE constraint at the database level so the rule holds no matter how the data arrives |

> Replace these with the problems you actually hit — that is what the viva
> asks about.

## 14. Future enhancements

- Login and role-based access, so only staff can delete records.
- Pagination once the register grows past a few hundred rows.
- A `Course` entity with a many-to-many link to students, plus marks per course.
- Export the register to CSV or PDF.
- Rebuild the frontend in React to practise component state.
- Deploy the backend and switch SQLite for PostgreSQL.

## 15. Repository

**Repository URL:** [paste your GitHub URL]

Commits were made after each working stage: project setup, model and migration,
API endpoints, frontend layout, API integration, validation, tests,
documentation.

---

## Viva preparation

Be ready to answer these in your own words:

1. Trace what happens when you press **Save student** — every step from the
   click to the row appearing in the table.
2. Why validate on both the client and the server?
3. What does the serializer do that the model does not?
4. What is CORS, and why did you need `django-cors-headers`?
5. Difference between PUT and PATCH.
6. Why does the ORM protect against SQL injection?
7. What does a 400 mean, and what does a 404 mean?
8. Why is `cgpa` DECIMAL and not FLOAT?
9. What would break if you removed the UNIQUE constraint on `roll_number`?
10. Where would you add authentication, and why there?

# API Documentation

Base URL: `http://127.0.0.1:8000/api`

All requests and responses use JSON. No authentication is required in the
development configuration.

## Endpoint summary

| Operation | Method | Endpoint | Success status |
|---|---|---|---|
| Create | POST | `/api/students/` | 201 Created |
| Read all | GET | `/api/students/` | 200 OK |
| Read one | GET | `/api/students/{id}/` | 200 OK |
| Update (full) | PUT | `/api/students/{id}/` | 200 OK |
| Update (partial) | PATCH | `/api/students/{id}/` | 200 OK |
| Delete | DELETE | `/api/students/{id}/` | 200 OK |
| Statistics | GET | `/api/stats/` | 200 OK |

## The Student resource

| Field | Type | Rules |
|---|---|---|
| `id` | integer | Read-only, assigned by the database |
| `roll_number` | string | Required, unique, max 15 chars, letters/digits/`-`/`/` |
| `full_name` | string | Required, min 3 chars, letters and `. ' -` only |
| `email` | string | Required, unique, valid email format |
| `phone` | string | Optional, exactly 10 digits when supplied |
| `department` | string | Required, one of `CSE`, `IT`, `ECE`, `EEE`, `MECH`, `CIVIL` |
| `year_of_study` | integer | Required, 1 to 4 |
| `cgpa` | decimal | Required, 0.00 to 10.00 |
| `created_at` | datetime | Read-only |
| `updated_at` | datetime | Read-only |

---

## Create

`POST /api/students/`

Request:

```json
{
  "roll_number": "21CSE045",
  "full_name": "Anitha Ramesh",
  "email": "anitha.r@example.edu",
  "phone": "9876543210",
  "department": "CSE",
  "year_of_study": 3,
  "cgpa": "8.75"
}
```

Response — `201 Created`:

```json
{
  "id": 1,
  "roll_number": "21CSE045",
  "full_name": "Anitha Ramesh",
  "email": "anitha.r@example.edu",
  "phone": "9876543210",
  "department": "CSE",
  "department_display": "Computer Science and Engineering",
  "year_of_study": 3,
  "cgpa": "8.75",
  "created_at": "2026-01-10T09:00:00+05:30",
  "updated_at": "2026-01-10T09:00:00+05:30"
}
```

## Read all

`GET /api/students/`

Optional query parameters:

| Parameter | Example | Effect |
|---|---|---|
| `search` | `?search=anitha` | Matches name, roll number or email |
| `department` | `?department=CSE` | Filters by department code |
| `year` | `?year=3` | Filters by year of study |
| `ordering` | `?ordering=-cgpa` | Sorts by `roll_number`, `full_name`, `cgpa` or `created_at`; prefix with `-` to reverse |

Returns a JSON array of student objects.

## Read one

`GET /api/students/1/` — returns a single student object, or `404` if the ID
does not exist.

## Update

`PUT /api/students/1/` replaces every field, so send the complete object.
`PATCH /api/students/1/` updates only the fields you send:

```json
{ "cgpa": "9.10" }
```

## Delete

`DELETE /api/students/1/`

Response — `200 OK`:

```json
{ "detail": "Student 21CSE045 deleted." }
```

## Statistics

`GET /api/stats/`

```json
{
  "total_students": 5,
  "average_cgpa": 8.13,
  "by_department": { "CSE": 2, "IT": 1, "ECE": 1, "MECH": 1 }
}
```

---

## Error format

Every error uses the same shape, so the frontend only parses one structure.

Validation failure — `400 Bad Request`:

```json
{
  "success": false,
  "message": "The request could not be processed. Check the fields below.",
  "errors": {
    "roll_number": ["Student with this roll number already exists."],
    "email": ["Enter a valid email address."],
    "year_of_study": ["Ensure this value is less than or equal to 4."],
    "cgpa": ["Ensure this value is less than or equal to 10."]
  }
}
```

Record not found — `404 Not Found`:

```json
{
  "success": false,
  "message": "No Student matches the given query.",
  "errors": {}
}
```

| Status | When it happens |
|---|---|
| 200 | Read, update or delete succeeded |
| 201 | Create succeeded |
| 400 | Validation failed |
| 404 | No record with that ID |
| 405 | Method not allowed on that URL |
| 500 | Unhandled server error |

## Testing with Postman

Import `docs/postman_collection.json`. It contains one request per endpoint
plus the negative cases (duplicate roll number, invalid email, out-of-range
CGPA, missing required field, non-existent ID) required by section 10 of the
SOP.

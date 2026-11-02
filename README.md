# Service Management Module

A service management module built with **Django** and **Django REST Framework**, backed by **SQLite**.

The module provides two independent interfaces over a single `Services` model:

- **REST API**: JSON endpoints for creating, listing, retrieving, updating and deleting services, with validation, pagination, search and status filtering.
- **HTML Management Panel**: a server-rendered interface built with Django views, forms and templates. It reads and writes the database directly and does not call the REST API.

---

## Table of Contents

1. [Requirements Coverage](#1-requirements-coverage)
2. [Technology Stack](#2-technology-stack)
3. [Installation and Setup](#3-installation-and-setup)
4. [Project Structure](#4-project-structure)
5. [Data Model](#5-data-model)
6. [REST API](#6-rest-api)
7. [HTML Management Panel](#7-html-management-panel)
8. [Testing](#8-testing)
9. [Deployment Configuration](#9-deployment-configuration)

---

## 1. Requirements Coverage

| # | Requirement | Implementation |
|---|-------------|----------------|
| 1 | Django app named `service` | `service/` |
| 2 | `Services` model with `service_name`, `description`, `price`, `duration`, `status`, `created_at`, `updated_at` | `service/models.py` |
| 3 | Create, List, Detail, Update and Delete APIs | `service/api/views.py`, `service/api/urls.py` |
| 4 | Input validation | `service/api/serializers.py` (API), `service/panel/forms.py` (HTML) |
| 5 | Invalid ID handling | `ServiceDetailView.get_object()` (API), `get_object_or_404` (HTML) |
| 6 | Appropriate HTTP status codes | 200, 201, 204, 400 and 404 (see [Status Codes](#status-codes)) |
| 7 | Pagination | `service/api/pagination.py` (API), Django `Paginator` (HTML) |
| 8 | Search by service name | `SearchFilter` (API), `q` parameter (HTML) |
| 9 | Filter by status | `DjangoFilterBackend` (API), `status` parameter (HTML) |
| 10 | HTML pages: List, Add, Edit, Details, Delete | `service/panel/`, `templates/service/` |
| 11 | Frontend search, active/inactive filter, pagination and form validation | `service_list` view, `ServiceForm` |
| 12 | REST API and HTML interface implemented separately | Separate `api/` and `panel/` packages; the panel does not call the API |
| 13 | SQLite database | `DATABASES` in `config/settings.py` |

---

## 2. Technology Stack

| Component | Version |
|-----------|---------|
| Python | 3.11 |
| Django | 5.2.5 |
| Django REST Framework | 3.16.1 |
| django-filter | 25.2 |
| Database | SQLite |
| UI styling | Bootstrap 5.3 (CDN) |

---

## 3. Installation and Setup

```bash
git clone https://github.com/VinayV01/Service_Management.git
cd Service_Management

python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser # optional, for Django admin
python manage.py runserver
```

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Home page |
| `http://127.0.0.1:8000/services/` | HTML Management Panel |
| `http://127.0.0.1:8000/api/services/` | REST API (DRF browsable interface) |
| `http://127.0.0.1:8000/admin/` | Django admin |

---

## 4. Project Structure

```
Service_Management/
├── config/                         # Project configuration
│   ├── settings.py
│   ├── urls.py                     # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
│
├── service/                        # Service application
│   ├── models.py                   # Services model
│   ├── admin.py                    # Django admin registration
│   ├── tests.py                    # API and panel test cases
│   ├── migrations/
│   │
│   ├── api/                        # REST API
│   │   ├── serializers.py          # Serialization and validation
│   │   ├── views.py                # Generic API views
│   │   ├── pagination.py           # Pagination class
│   │   └── urls.py
│   │
│   └── panel/                      # HTML Management Panel
│       ├── forms.py                # ModelForm and validation
│       ├── views.py                # Function-based views
│       └── urls.py
│
├── templates/
│   ├── base.html                   # Base layout
│   ├── home.html                   # Home page
│   ├── 404.html                    # Not-found page
│   ├── includes/                   # Shared partials (messages, pagination)
│   └── service/                    # List, detail, form and delete templates
│
├── static/
│   ├── css/style.css
│   └── js/script.js                # Auto-dismisses flash messages
│
├── manage.py
└── requirements.txt
```

The REST API (`service/api/`) and the HTML panel (`service/panel/`) are in separate packages. The only thing they share is the `Services` model.

---

## 5. Data Model

**Model:** `Services` · **Table:** `services` · **Default ordering:** `-created_at`

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | BigAutoField | Primary key |
| `service_name` | CharField(100) | Required, unique, minimum 3 characters |
| `description` | TextField | Optional |
| `price` | DecimalField(10, 2) | Required, greater than 0 |
| `duration` | PositiveIntegerField | Required, in minutes, 1 to 1440 |
| `status` | CharField(10) | `active` or `inactive`, default `active` |
| `created_at` | DateTimeField | Set automatically on creation |
| `updated_at` | DateTimeField | Updated automatically on every save |

---

## 6. REST API

**Base URL:** `/api/services/`

### Endpoints

| Operation | Method | Endpoint | Success Response |
|-----------|--------|----------|------------------|
| Create Service | `POST` | `/api/services/` | `201 Created` |
| List Services | `GET` | `/api/services/` | `200 OK` |
| Service Details | `GET` | `/api/services/{id}/` | `200 OK` |
| Update Service | `PUT` / `PATCH` | `/api/services/{id}/` | `200 OK` |
| Delete Service | `DELETE` | `/api/services/{id}/` | `204 No Content` |

The endpoints use DRF generic views: `ListCreateAPIView` for the collection and `RetrieveUpdateDestroyAPIView` for single records.

### Query Parameters (List)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `page` | Page number | `?page=2` |
| `page_size` | Records per page (default 5, maximum 50) | `?page_size=10` |
| `search` | Case-insensitive search on `service_name` | `?search=hair` |
| `status` | Filter by status (`active` / `inactive`) | `?status=active` |
| `ordering` | Sort by `service_name`, `price`, `duration` or `created_at` | `?ordering=-price` |

Parameters can be combined, for example `/api/services/?search=cut&status=active&page=1`.

### Validation Rules

| Field | Rule |
|-------|------|
| `service_name` | Minimum 3 characters after trimming whitespace; must be unique (case-insensitive) |
| `price` | Must be greater than 0 |
| `duration` | Must be between 1 and 1440 minutes |
| `status` | Must be `active` or `inactive` |

### Invalid ID Handling

| Scenario | Request | Response |
|----------|---------|----------|
| Non-numeric ID | `GET /api/services/abc/` | `400` `{"detail": "Service ID must be a positive number."}` |
| Non-existent ID | `GET /api/services/999/` | `404` `{"detail": "Service with ID 999 not found."}` |

### Status Codes

| Code | Meaning |
|------|---------|
| `200 OK` | Successful retrieval or update |
| `201 Created` | Service created |
| `204 No Content` | Service deleted |
| `400 Bad Request` | Validation failure, non-numeric ID or invalid filter value |
| `404 Not Found` | Service does not exist, or the page number is out of range |
| `405 Method Not Allowed` | HTTP method not supported by the endpoint |

### Example: Create Service

**Request**

```http
POST /api/services/
Content-Type: application/json

{
    "service_name": "Hair Cut",
    "description": "Basic hair cut",
    "price": 200,
    "duration": 30,
    "status": "active"
}
```

**Response: `201 Created`**

```json
{
    "id": 1,
    "service_name": "Hair Cut",
    "description": "Basic hair cut",
    "price": "200.00",
    "duration": 30,
    "status": "active",
    "created_at": "2026-11-02T10:15:00+05:30",
    "updated_at": "2026-11-02T10:15:00+05:30"
}
```

### Example: Validation Error

**Response: `400 Bad Request`**

```json
{
    "service_name": ["Service name must have at least 3 characters."],
    "price": ["Price must be greater than 0."]
}
```

### Example: Paginated List

**Response: `200 OK`**

```json
{
    "count": 12,
    "next": "http://127.0.0.1:8000/api/services/?page=2",
    "previous": null,
    "results": [ ... ]
}
```

---

## 7. HTML Management Panel

**Base URL:** `/services/`

### Pages

| Page | URL | View |
|------|-----|------|
| Home | `/` | `home` |
| Service List | `/services/` | `service_list` |
| Add Service | `/services/add/` | `service_create` |
| Service Details | `/services/{id}/` | `service_detail` |
| Edit Service | `/services/{id}/edit/` | `service_update` |
| Delete Service | `/services/{id}/delete/` | `service_delete` |

### Features

- **Search:** case-insensitive partial match on service name (`?q=`).
- **Status filter:** shows active or inactive services only (`?status=`).
- **Pagination:** 5 records per page, set by `SERVICES_PER_PAGE`. The search and filter parameters are kept when moving between pages.
- **Form validation:** `ServiceForm` (a `ModelForm`) applies the same rules as the API. Errors are shown next to each field, and the values the user entered are kept.
- **Delete confirmation:** records are deleted only by a `POST` from a confirmation page.
- **Invalid IDs:** `get_object_or_404` returns a 404 response for records that don't exist.
- **Feedback messages:** the Django messages framework confirms create, update and delete actions.
- **Security:** every form includes CSRF protection.

### Separation from the REST API

The panel uses Django views, forms and templates only. Every page is rendered on the server from direct ORM queries. The panel makes no JavaScript requests to the REST API. The only JavaScript in the project (`static/js/script.js`) dismisses flash messages.

| Aspect | REST API | HTML Panel |
|--------|----------|------------|
| Package | `service/api/` | `service/panel/` |
| Views | DRF generic class-based views | Django function-based views |
| Validation | `ServiceSerializer` | `ServiceForm` |
| Pagination | `PageNumberPagination` | `django.core.paginator.Paginator` |
| Search / Filter | `SearchFilter`, `DjangoFilterBackend` | ORM queryset filtering |
| Output | JSON | HTML |

---

## 8. Testing

The test suite in `service/tests.py` has 19 test cases. They cover:

- **REST API:** create, validation errors, duplicate names, pagination, out-of-range pages, search, status filter, invalid filter values, retrieve, invalid IDs (400 / 404), partial update and delete.
- **HTML panel:** home page counts, list rendering, search and filter, create (valid and invalid input), update, delete, and 404 handling.

```bash
python manage.py test service
```

---

## 9. Deployment Configuration

Production settings are read from environment variables. When a variable is not set, the development default is used.

| Variable | Purpose | Development Default |
|----------|---------|---------------------|
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DJANGO_SECRET_KEY` | Secret key | Development key |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names | `127.0.0.1,localhost` |

Before deploying, collect the static files into `STATIC_ROOT` (`staticfiles/`):

```bash
python manage.py collectstatic --noinput
```

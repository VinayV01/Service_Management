# Service Management Module

A small Django project for managing services: add, view, edit, delete, search and filter them.

It has two separate parts:

1. **REST API**, built with Django REST Framework. It returns JSON.
2. **HTML Management Panel**, built with normal Django views, forms and templates. It does not use JavaScript or the API.

Both parts use the same model (`Services`) and the same SQLite database.

---

## 0. The Task

The task was to build a basic **Service Management Module** with Django and Django REST Framework. A "service" here is something a business offers, such as a hair cut or a massage, with a price and a duration. The module has to let you create, view, update and delete these services in two separate ways.

The task has three parts.

**Part 1: Database model**

- Create a Django app named `service`.
- Create a model named `Services` with these fields: `service_name`, `description`, `price`, `duration`, `status`, `created_at`, `updated_at`.

**Part 2: REST API**

- Build five APIs: Create Service, List Services, Service Details, Update Service and Delete Service.
- The APIs must:
  - validate the input data
  - handle invalid IDs (an ID that doesn't exist, or one that isn't a number)
  - return the correct HTTP status codes (200, 201, 204, 400, 404)
  - paginate the list
  - support search by service name
  - support filtering by status

**Part 3: HTML admin panel**

- Build a separate web interface using Django views, forms and templates, with these pages: Service List, Add Service, Edit Service, Service Details and Delete Service.
- The pages must support search by name, active/inactive filtering, pagination and form validation.

**Rules**

- The REST API and the HTML panel must be built separately. The HTML pages must use Django views, forms and templates. They must not use JavaScript to call the REST API.
- SQLite must be used as the database.

### Where each requirement is done

| Requirement | Where it is done |
|-------------|------------------|
| App named `service` | `service/` folder |
| `Services` model with all 7 fields | `service/models.py` |
| Create / List / Detail / Update / Delete APIs | `service/api/views.py`, `service/api/urls.py` |
| API validation | `service/api/serializers.py` |
| Invalid ID handling (API) | `ServiceDetailView.get_object()` in `service/api/views.py` |
| Proper status codes | Built into the DRF generic views, plus the custom 400/404 responses for bad IDs |
| API pagination | `service/api/pagination.py` |
| API search and status filter | `search_fields` and `filterset_fields` in `service/api/views.py` |
| HTML pages (list, add, edit, detail, delete) | `service/panel/views.py` and `templates/service/` |
| HTML search, filter, pagination | `service_list` view in `service/panel/views.py` |
| Form validation | `service/panel/forms.py` |
| API and HTML kept separate | Two folders, `service/api/` and `service/panel/`, with no JavaScript calls to the API |
| SQLite | `DATABASES` in `config/settings.py` |

---

## 1. Setup and Run

```bash
# (optional) create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / Mac

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # optional, only for /admin
python manage.py runserver
```

Open in the browser:

| URL | What it is |
|-----|-----------|
| http://127.0.0.1:8000/ | Home / intro page |
| http://127.0.0.1:8000/services/ | HTML management panel |
| http://127.0.0.1:8000/api/services/ | REST API (DRF browsable API) |
| http://127.0.0.1:8000/admin/ | Django default admin |

Run the tests:

```bash
python manage.py test service
```

---

## 2. Folder Structure

```
ServiceManagement/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── config/                     # project settings
│   ├── settings.py             # installed apps, DB, DRF settings
│   ├── urls.py                 # main url file (connects api + panel)
│   ├── wsgi.py
│   └── asgi.py
│
├── service/                    # the "service" app
│   ├── models.py               # Services model (database table)
│   ├── admin.py                # registers model in Django admin
│   ├── tests.py                # tests for API and HTML panel
│   ├── migrations/             # auto generated DB migrations
│   │
│   ├── api/                    # ---- REST API part ----
│   │   ├── serializers.py      # converts model <-> JSON + validation
│   │   ├── views.py            # API views (CRUD)
│   │   ├── pagination.py       # pagination settings for API
│   │   └── urls.py             # API routes
│   │
│   └── panel/                  # ---- HTML panel part ----
│       ├── forms.py            # ModelForm + validation
│       ├── views.py            # list / add / edit / detail / delete views
│       └── urls.py             # panel routes
│
├── templates/
│   ├── base.html               # common layout (navbar, messages)
│   ├── home.html               # intro page with service counts
│   ├── 404.html                # page shown when an ID doesn't exist (DEBUG=False)
│   ├── includes/
│   │   ├── messages.html       # success / error alerts
│   │   └── pagination.html     # reusable pagination buttons
│   └── service/
│       ├── service_list.html
│       ├── service_form.html   # used for both Add and Edit
│       ├── service_detail.html
│       └── service_confirm_delete.html
│
└── static/
    ├── css/style.css
    └── js/script.js            # only auto-hides the alert messages
```

**Why this layout?** The API code and the HTML panel code are in two separate folders (`api/` and `panel/`), so the two parts stay apart, as the task asks. The model is shared and lives in `service/models.py`.

---

## 3. Database Model

File: `service/models.py`

| Field | Type | Notes |
|-------|------|-------|
| `id` | Auto | Primary key, created automatically |
| `service_name` | CharField(100) | Required, unique |
| `description` | TextField | Optional |
| `price` | DecimalField(10, 2) | Required, must be > 0 |
| `duration` | PositiveIntegerField | In minutes, 1 to 1440 |
| `status` | CharField | `active` or `inactive` (default `active`) |
| `created_at` | DateTimeField | Set once when the record is created (`auto_now_add`) |
| `updated_at` | DateTimeField | Updated on every save (`auto_now`) |

- The table name is `services`.
- Records are ordered newest first (`ordering = ['-created_at']`).
- `STATUS_ACTIVE` / `STATUS_INACTIVE` constants are used so the strings are not repeated everywhere.

---

## 4. REST API

Base URL: `/api/services/`

| Action | Method | URL | Success code |
|--------|--------|-----|--------------|
| Create Service | POST | `/api/services/` | 201 Created |
| List Services | GET | `/api/services/` | 200 OK |
| Service Details | GET | `/api/services/<id>/` | 200 OK |
| Update Service (full) | PUT | `/api/services/<id>/` | 200 OK |
| Update Service (partial) | PATCH | `/api/services/<id>/` | 200 OK |
| Delete Service | DELETE | `/api/services/<id>/` | 204 No Content |

### How it works

- `ServiceListCreateView` (a `ListCreateAPIView`) handles **list** and **create**.
- `ServiceDetailView` (a `RetrieveUpdateDestroyAPIView`) handles **detail**, **update** and **delete**.
- These DRF generic views already contain the CRUD logic, so the code stays short.

### Validation (in `serializers.py`)

| Field | Rule |
|-------|------|
| service_name | At least 3 characters, extra spaces removed, no duplicates (case-insensitive, so "Hair Cut" and "hair cut" count as the same) |
| price | Must be greater than 0 |
| duration | Must be between 1 and 1440 minutes |
| status | Must be `active` or `inactive` (checked by the model choices) |

If validation fails, the API returns **400 Bad Request** with the error for each field:

```json
{
    "service_name": ["Service name must have at least 3 characters."],
    "price": ["Price must be greater than 0."]
}
```

### Invalid ID handling

`get_object()` is overridden in `ServiceDetailView`:

| Case | Example | Response |
|------|---------|----------|
| ID is not a number | `/api/services/abc/` | 400: `{"detail": "Service ID must be a positive number."}` |
| ID does not exist | `/api/services/999/` | 404: `{"detail": "Service with ID 999 not found."}` |

### Pagination, Search, Filter

These are set up in `settings.py` under `REST_FRAMEWORK` and in the view.

| Feature | Query param | Example |
|---------|-------------|---------|
| Pagination | `page`, `page_size` (max 50) | `/api/services/?page=2&page_size=10` |
| Search by name | `search` | `/api/services/?search=hair` |
| Filter by status | `status` | `/api/services/?status=active` |
| Ordering (extra) | `ordering` | `/api/services/?ordering=-price` |

They can be combined: `/api/services/?search=cut&status=active&page=1`

Example list response:

```json
{
    "count": 12,
    "next": "http://127.0.0.1:8000/api/services/?page=2",
    "previous": null,
    "results": [
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
    ]
}
```

### Example create request

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

You can test all of these from the browser at `/api/services/` (DRF browsable API), or with Postman.

### Status codes used

| Code | When |
|------|------|
| 200 OK | List, detail, update successful |
| 201 Created | Service created |
| 204 No Content | Service deleted |
| 400 Bad Request | Validation error, non-numeric ID, wrong status filter value |
| 404 Not Found | Service ID doesn't exist, or the page number is out of range |
| 405 Method Not Allowed | Wrong HTTP method (e.g. DELETE on the list URL) |

---

## 5. HTML Management Panel

Base URL: `/services/`

| Page | URL | View function |
|------|-----|---------------|
| Home (intro) | `/` | `home` |
| Service List | `/services/` | `service_list` |
| Add Service | `/services/add/` | `service_create` |
| Service Details | `/services/<id>/` | `service_detail` |
| Edit Service | `/services/<id>/edit/` | `service_update` |
| Delete Service | `/services/<id>/delete/` | `service_delete` |

Simple function-based views are used so the flow is easy to follow: **GET** shows the page and **POST** saves the data.

### Features

- **Home page**: a short intro to the project, with the total, active and inactive counts, and links to the panel and the API. Clicking the Active or Inactive count opens the list already filtered by that status.
- **Search by name**: the `q` box on the list page uses `service_name__icontains`, so the search is case-insensitive and matches part of the name.
- **Active / Inactive filter**: the status dropdown filters by `status`.
- **Pagination**: Django's `Paginator` shows 5 records per page (`SERVICES_PER_PAGE` in settings). The search and filter values stay the same when you change pages, because the view builds `query_string` from the current GET params.
- **Form validation**: `ServiceForm` (a `ModelForm`) checks the same rules as the API: name length, unique name, price > 0, duration 1 to 1440. Errors appear under each field, and the values you typed stay in the form.
- **Delete confirmation**: Delete first opens a confirm page. The record is deleted only after you submit the form there (POST). A plain GET request never deletes anything.
- **Success messages**: Django's messages framework shows alerts like "Service added successfully". Each alert has a close (×) button and fades out on its own after 3 seconds (`static/js/script.js`). This is the only JavaScript in the project, and it only hides the alert. It never calls the API.
- **Invalid IDs**: `get_object_or_404` returns a 404 page if the service doesn't exist. The URLs use `<int:pk>`, so non-numeric IDs also give 404.
- **CSRF protection**: every form has `{% csrf_token %}`.

### Flow example: Add Service

1. The user opens `/services/add/`. This is a GET request, so an empty form is shown.
2. The user fills in the form and submits it. This is a POST request.
3. `form.is_valid()` runs all the validation rules.
   - If the data is valid, the service is saved, a success message is set, and the user is redirected to the list page.
   - If not, the same page is shown again with error messages.

Edit works the same way, except that the form is filled with the existing record (`instance=service`).

---

## 6. API vs HTML Panel

| | REST API | HTML Panel |
|---|---|---|
| Folder | `service/api/` | `service/panel/` |
| Built with | DRF generic views | Django function views |
| Validation | Serializer | ModelForm |
| Output | JSON | HTML templates |
| Pagination | DRF `PageNumberPagination` | Django `Paginator` |
| Search / Filter | `SearchFilter` + `DjangoFilterBackend` | Queryset filter in the view |

The two parts share only the model. The HTML panel never calls the API.

---

## 7. Tests

File: `service/tests.py`. There are 17 tests in total.

- **API tests**: create, validation errors, duplicate name, pagination, search, status filter, detail, invalid IDs (404 / 400), update, delete.
- **Panel tests**: home page counts, list page, search and filter, add (valid and invalid), edit, delete, and 404 for an invalid ID.

```bash
python manage.py test service
```

---

## 8. Tech Used

- Python 3.11
- Django 5.2
- Django REST Framework 3.16
- django-filter (for `?status=` filtering in the API)
- SQLite
- Bootstrap 5 (loaded from a CDN, only for styling)

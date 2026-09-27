# TeamBoard

TeamBoard is a B2B Knowledge Base API platform. Companies register, receive an
API key and JWT, and query a curated Q&A knowledge base covering APIs,
databases, cloud infrastructure, and backend frameworks. Every query is
logged so platform admins can see usage stats via a dashboard endpoint.

## Stack

- Django 6.1 + Django REST Framework
- PostgreSQL (via Docker)
- SimpleJWT for authentication

## Setup

### 1. Clone and create a virtual environment

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and adjust values if needed:

```bash
cp .env.example .env
```

`.env` is never committed — all secrets and DB credentials live there and are
loaded via `python-dotenv` in `config/settings.py`.

### 3. Start PostgreSQL (and PGAdmin) via Docker

```bash
docker compose up -d db pgadmin
```

- Postgres is exposed on `localhost:${POSTGRES_PORT}` (default `5433` — `5432`
  is a common default that may already be in use on your machine).
- PGAdmin is available at [http://localhost:5050](http://localhost:5050)
  (login: `admin@teamboard.com` / `admin`). Register a new server in PGAdmin
  pointing at host `db`, port `5432`, using the credentials from `.env`.

### 4. Apply migrations

```bash
python manage.py migrate
```

This creates the `Company`, `KBEntry`, and `QueryLog` tables (verify in
PGAdmin under the `teamboard` database).

### 5. Seed the knowledge base

```bash
python manage.py seed_kb
```

This loads 12 sample Q&A entries across the API, Database, Cloud, and
Framework categories (idempotent — safe to re-run).

### 6. Run the server

```bash
python manage.py runserver
```

The API is now available at `http://localhost:8000/api/`.

## How registration works

Registration only takes a username, password, company name, and optional
email. A `post_save` signal on Django's `User` model (see `api/signals.py`)
automatically creates the linked `Company` profile and generates its
`api_key` using `secrets.token_urlsafe(32)` — this never happens in the view,
so every user is guaranteed a company profile and API key the moment their
account exists. The signal is wired up in `api/apps.py` via `AppConfig.ready()`.

> **Note on creation detection:** the signal uses the `created` boolean that
> Django's `post_save` signal provides, not `instance._state.adding`.
> Empirically, Django sets `_state.adding = False` on the instance *before*
> dispatching `post_save` (see `django/db/models/base.py`), so checking it
> inside a `post_save` receiver reads `False` on both create and update — it
> cannot distinguish the two. `created` is the mechanism Django provides
> specifically for this purpose and is what's implemented here.

## Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | Public | Register a company, returns JWT + api_key |
| POST | `/api/auth/login/` | Public | Log in, returns a fresh JWT |
| POST | `/api/kb/query/` | JWT required | Search the knowledge base, logs the query |
| GET | `/api/admin/usage-summary/` | JWT + Admin role | Platform-wide usage stats |

All endpoints require a JWT `Authorization: Bearer <token>` header by default
(`REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES` in `settings.py`); register and
login explicitly opt out with `authentication_classes = []` and
`permission_classes = []`.

To test the admin endpoint, promote a company to admin directly in PGAdmin
(or the Django shell):

```python
from api.models import Company
c = Company.objects.get(user__username="acmecorp")
c.role = Company.Role.ADMIN
c.save()
```

## Postman collection

Import `TeamBoard.postman_collection.json` into Postman. It covers all 11
required scenarios (register, duplicate register, login success/failure,
KB query with/without token, matching/non-matching search, missing search
field, and admin usage summary as both a CLIENT and an ADMIN). Run requests
1 and 3 first so the collection variables `client_access` and `client_api_key`
are populated automatically.

Request 10 (admin usage summary) needs an admin-authorized token in
`admin_access`, which is *not* set automatically — there's no API endpoint
to promote a company to admin, by design. Before running it:

1. Promote the `acmecorp` company's role in PGAdmin or the Django shell:
   ```python
   from api.models import Company
   c = Company.objects.get(user__username="acmecorp")
   c.role = Company.Role.ADMIN
   c.save()
   ```
2. Run request **"9b. Login as Admin"** — it logs back in as `acmecorp` and
   captures the resulting token into `admin_access`.
3. Now run request 10.

If you skip step 1, request 9b will still succeed (it's just a login call)
but the resulting token won't have admin rights, and 10 will 403.

Request 11 is not an API call — it's a reminder to open PGAdmin and confirm
rows exist in the `query_logs` table after running requests 6 and 7.

## Project structure

```
config/          Django project settings, root URLconf
api/
  models.py      Company, KBEntry, QueryLog
  signals.py     post_save signal: auto-creates Company + api_key
  serializers.py Request/response validation
  views.py       RegisterView, LoginView, KBQueryView, UsageSummaryView
  permissions.py IsAdminUser custom permission
  management/commands/seed_kb.py
```

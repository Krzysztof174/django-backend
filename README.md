# BookaBook - Krzysztof Osiniak 174903

Community library REST API built with Django and Django REST Framework.
Members borrow physical book copies, librarians manage the catalog and
oversee loans.

## Domain model

| Model | Purpose | Relations |
|---|---|---|
| `Profile` | Library card data (phone, loan limit) | one-to-one with `User` |
| `Author` | Book author | – |
| `Genre` | Book category | – |
| `Book` | Catalog entry identified by ISBN | FK `Author`, M2M `Genre` |
| `Copy` | Physical copy with inventory code and status | FK `Book` |
| `Loan` | Borrowing of a copy by a user | FK `Copy`, FK `User` |

User roles are Django groups: `Members` and `Librarians`.

## Requirements

- Docker with Docker Compose v2

Everything runs inside containers; no local Python installation is needed.

## Getting started

```bash
docker compose up --build
```

Migrations are applied automatically on container start. The app is
available at <http://localhost:8000/admin/>.

The SQLite database is stored in the `sqlite_data` named volume, so it
survives container restarts. Use `docker compose down -v` to reset it.

## Common commands

Create an admin account:

```bash
docker compose run --rm web python manage.py createsuperuser
```

Create migrations after changing models:

```bash
docker compose run --rm web python manage.py makemigrations
```

Apply migrations manually:

```bash
docker compose run --rm web python manage.py migrate
```

Run tests (uses an isolated in-memory database):

```bash
docker compose run --rm web python manage.py test
```

Lint and format:

```bash
docker compose run --rm web ruff check .
docker compose run --rm web ruff format .
```

## Configuration

| Variable | Description | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (required) | random string |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host list | `localhost,127.0.0.1` |
| `SQLITE_PATH` | SQLite file path (set by Compose) | `/app/data/db.sqlite3` |

## API documentation

Swagger UI will be available at <http://localhost:8000/api/docs/>
(planned for a later milestone).

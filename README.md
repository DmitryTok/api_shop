[![Python](https://img.shields.io/badge/-Python-%233776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0a)](https://www.python.org/)
[![Django Rest Framework](https://img.shields.io/badge/-Django%20Rest%20Framework-%2300B96F?style=for-the-badge&logo=django&logoColor=white&labelColor=0a0a0a)](https://www.django-rest-framework.org/)
[![JWT Authentication](https://img.shields.io/badge/-JWT%20Authentication-%23FFB300?style=for-the-badge&logo=json-web-tokens&logoColor=white&labelColor=0a0a0a)](https://jwt.io/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-%23316192?style=for-the-badge&logo=postgresql&logoColor=white&labelColor=0a0a0a)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/-Docker-%232496ED?style=for-the-badge&logo=docker&logoColor=white&labelColor=0a0a0a)](https://www.docker.com/)
[![Swagger](https://img.shields.io/badge/-Swagger-%2385EA2D?style=for-the-badge&logo=swagger&logoColor=white&labelColor=0a0a0a)](https://swagger.io/)
[![pre-commit](https://img.shields.io/badge/-pre--commit-yellow?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=0a0a0a)](https://pre-commit.com/)
[![Ruff](https://img.shields.io/badge/-Ruff-%23E10098?style=for-the-badge&logo=ruff&logoColor=white&labelColor=0a0a0a)](https://docs.astral.sh/ruff/)
[![isort](https://img.shields.io/badge/isort-enabled-brightgreen?style=for-the-badge&logo=isort&logoColor=white&labelColor=0a0a0a)](https://pycqa.github.io/isort/)

# WearlyShop API

Django REST Framework backend for the WearlyShop e-commerce store. The frontend is a separate app (not in this repo).

For deployment topology, the Celery worker, and Sentry, see [`docs/infra.md`](docs/infra.md).

## Run the project

---

### Create a `.env` file

Copy `.env.example` to `.env` and fill it in — it documents every variable `settings.py` reads, including security, Sentry, Cloudinary, Celery/Redis, and email (Resend). The minimal set to get a local stack running:

```
APP_ENV=local
DEBUG=true

SECRET=<a long random secret>
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=api_shop
DB_USER=postgres
DB_PASSWORD=<database password>
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0

SUPER_LOGIN=<superuser email, optional>
SUPER_PASSWORD=<superuser password, optional>
```

Leave `SENTRY_DSN` and the `CLOUDINARY_*` vars empty for local dev unless you specifically need them (Sentry never sends events when `APP_ENV=local`, regardless of `SENTRY_DSN`; media uploads will fail without Cloudinary credentials).

### Run docker-compose

```
docker compose up --build --force-recreate
```

This starts Postgres, Redis, the Django dev server, and an nginx reverse proxy in front of it — all on `http://localhost:8080`. It only runs `collectstatic` and `migrate` on boot; it does **not** seed any data.

### Seed data (optional, manual)

```
make seed         # products, categories, brands, variants, discounts, terms
make seed-users   # 11 demo users (requires load_terms to have run first)
make superuser    # creates SUPER_LOGIN/SUPER_PASSWORD as a superuser
```

Each of these targets is idempotent-guarded and safe to re-run.

### Run background email tasks (Celery)

Sending activation/password-reset emails is fire-and-forget via Celery, but **no worker runs automatically** — `docker-compose.yml` does not define one. Without a worker, emails are silently never sent. To process the queue locally:

```
uv run celery -A api_shop worker -l info
```

Run it from the `api_shop/` directory (i.e. `api_shop/api_shop/`'s parent), with the same `.env` loaded.

---

### To stop the containers

```
ctrl + C
```

or, from another terminal:

```
docker compose stop
```

### To remove the containers and volumes

```
docker compose down -v
```

## Links

```text
--------------------------------------------------------------|
| Resource    |                      URL                      |
| ----------- | --------------------------------------------- |
| Admin Panel |  http://localhost:8080/admin/                 |
| --------    | --------------------------------------------- |
| Swagger     |  http://localhost:8080/api/schema/swagger-ui/ |
| --------    | --------------------------------------------- |
| Redoc       |  http://localhost:8080/api/schema/redoc/      |
| --------    | --------------------------------------------- |
| Health      |  http://localhost:8080/health/                |
| --------    | --------------------------------------------- |
```

## Tests and linting

```
uv sync --group dev
uv run pytest
uv run ruff check --fix .
uv run ruff format .
uv run pre-commit run --all-files
```

Tests require a reachable Postgres **and** Redis (nothing is mocked).

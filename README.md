[![Python](https://img.shields.io/badge/-Python-%233776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0a)](https://www.python.org/)
[![Django Rest Framework](https://img.shields.io/badge/-Django%20Rest%20Framework-%2300B96F?style=for-the-badge&logo=django&logoColor=white&labelColor=0a0a0a)](https://www.django-rest-framework.org/)
[![JWT Authentication](https://img.shields.io/badge/-JWT%20Authentication-%23FFB300?style=for-the-badge&logo=json-web-tokens&logoColor=white&labelColor=0a0a0a)](https://jwt.io/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-%23316192?style=for-the-badge&logo=postgresql&logoColor=white&labelColor=0a0a0a)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/-Docker-%232496ED?style=for-the-badge&logo=docker&logoColor=white&labelColor=0a0a0a)](https://www.docker.com/)
[![Swagger](https://img.shields.io/badge/-Swagger-%2385EA2D?style=for-the-badge&logo=swagger&logoColor=white&labelColor=0a0a0a)](https://swagger.io/)
[![pre-commit](https://img.shields.io/badge/-pre--commit-yellow?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=0a0a0a)](https://pre-commit.com/)
[![Ruff](https://img.shields.io/badge/-Ruff-%23E10098?style=for-the-badge&logo=ruff&logoColor=white&labelColor=0a0a0a)](https://docs.astral.sh/ruff/)
[![isort](https://img.shields.io/badge/isort-enabled-brightgreen?style=for-the-badge&logo=isort&logoColor=white&labelColor=0a0a0a)](https://pycqa.github.io/isort/)

# Online shop

## Run the project

---

### Create .env file and fill with required data

```
SECRET=<SECRET_KEY>
DB_ENGINE=<DB ENGINE postgres, mysql ...>
DB_NAME=<database name>
DB_USER=<database user>
DB_PASSWORD=<database password>
DB_HOST=<database host>
DB_PORT=<database port>

SUPER_LOGIN=superuser-email
SUPER_PASSWORD=superuser-password
```

### Run docker-compose file

```
docker compose up --build --force-recreate
```

---

### To stop container

```
ctrl + C
```

### To stop container

```
docker-compose stop
```

### To delete container

```
docker-compose down -v
```

# Links

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
| Mailpit     |  http://localhost:8025                        |
| --------    | --------------------------------------------- |
```

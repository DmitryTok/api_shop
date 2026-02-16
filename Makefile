MANAGE = api_shop/manage.py


makemigrations:
	python $(MANAGE) makemigrations

migrate:
	python $(MANAGE) migrate

run: makemigrations migrate
	python $(MANAGE) runserver

up:
	docker compose up --build --force-recreate

down:
	docker compose down -v
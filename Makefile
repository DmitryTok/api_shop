MANAGE = api_shop/manage.py

up:
	docker compose up --build --force-recreate

down:
	docker compose down -v

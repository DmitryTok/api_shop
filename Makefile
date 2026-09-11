MANAGE = api_shop/manage.py

up:
	docker compose up --build --force-recreate

down:
	docker compose down -v

seed:
	docker compose exec web python $(MANAGE) load_data
	docker compose exec web python $(MANAGE) load_terms

seed-users:
	docker compose exec web python $(MANAGE) load_users

superuser:
	docker compose exec web python $(MANAGE) create_default_superuser

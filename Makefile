MANAGE = api_shop/manage.py

up:
	docker compose up --build --force-recreate

down:
	docker compose down -v

seed:
	docker compose exec web python $(MANAGE) load_reference_data

superuser:
	docker compose exec web python $(MANAGE) create_default_superuser

poetry run alembic revision --autogenerate -m "initial tables"
poetry run alembic upgrade head

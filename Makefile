lint:
	poetry run flake8 vpn_routes

build:
	poetry build

main:
	poetry run python -m vpn_routes.main


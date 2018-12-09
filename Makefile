dev-tests:
	pipenv run python -m unittest

dev-format:
	pipenv run black app
	pipenv run flake8 --ignore="E501,E266,W503" app

start-flask:
	pipenv run flask run

db-init:
	pipenv run flask db init

db-update:
	pipenv run flask db migrate
	pipenv run flask db upgrade

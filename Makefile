dev-tests:
	pipenv run python -m unittest

dev-format:
	pipenv run black seatingchart
	pipenv run flake8 --ignore="E501,E266,W503" seatingchart

start-flask:
	pipenv run flask run
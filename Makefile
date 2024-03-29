test:
	poetry run pytest .

bandit:
	bandit -c pyproject.toml -r .

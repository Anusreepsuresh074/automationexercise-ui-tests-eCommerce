.PHONY: install lint typecheck test smoke parallel report docker-build docker-test

install:  ## Install dependencies, browsers and the pre-commit hook
	pip install -r requirements-dev.txt
	playwright install --with-deps
	pre-commit install

lint:  ## Lint and format-check
	ruff check .
	ruff format --check .

typecheck:  ## Static type check
	mypy

test:  ## Full suite (BROWSER=chromium|firefox|webkit)
	pytest --browser=$(or $(BROWSER),chromium)

smoke:  ## Smoke tier only
	pytest -m smoke --browser=$(or $(BROWSER),chromium)

parallel:  ## Full suite across all CPU cores
	pytest -n auto --browser=$(or $(BROWSER),chromium)

report:  ## Build and open the Allure report
	allure generate reports/allure-results --clean -o reports/allure-report
	allure open reports/allure-report

docker-build:  ## Build the test runner image
	docker build -t ui-tests .

docker-test:  ## Run the smoke tier in Docker
	docker run --rm --env-file .env ui-tests -m smoke -n 4

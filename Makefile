# TorchSigGUI development tasks
# Run `make help` to list the available targets

PYTHON ?= python
NPM ?= npm

.DEFAULT_GOAL := help
.PHONY: help install install-api install-web dev-api dev-web build-web test lint lint-api lint-web check check-webbuild package clean

help: ## List the available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: install-api install-web ## Install the API and interface development dependencies

install-api: ## Install the Python package in editable mode with development dependencies
	$(PYTHON) -m pip install -e ".[dev]"

install-web: ## Install the interface dependencies from the lockfile
	$(NPM) ci

dev-api: ## Start the API development server (reloads on changes)
	torchsiggui --dev

dev-web: ## Start the interface development server
	$(NPM) run dev

build-web: ## Build the interface into torchsiggui/webbuild
	$(NPM) run build

test: ## Run the API tests
	$(PYTHON) -m pytest

lint: lint-api lint-web ## Run all linters and the type check

lint-api: ## Lint the Python code with ruff
	ruff check .

lint-web: ## Lint and type check the interface
	$(NPM) run lint
	npx tsc --noEmit

check: lint test build-web check-webbuild ## Run the same checks as CI

check-webbuild: ## Fail if torchsiggui/webbuild differs from the committed build, ignoring chunk hashes
	$(PYTHON) scripts/check_webbuild.py

package: build-web ## Build the wheel and sdist into dist/
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build

clean: ## Remove build, test, and cache artifacts
	rm -rf build dist *.egg-info .next .pytest_cache .ruff_cache .coverage coverage.xml report.xml tsconfig.tsbuildinfo
	rm -rf tests/.pytest_cache tests/.coverage tests/coverage.xml tests/report.xml
	find . -name __pycache__ -type d -not -path './node_modules/*' -not -path './.venv/*' -exec rm -rf {} +

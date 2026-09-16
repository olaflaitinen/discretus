.PHONY: help install install-dev test test-cov lint format type security docs docs-clean bench clean build release precommit

PYTHON ?= python
PIP ?= $(PYTHON) -m pip

help:
	@echo "Available targets:"
	@echo "  install      install the library"
	@echo "  install-dev  install the library with the development extra"
	@echo "  test         run the test suite"
	@echo "  test-cov     run the test suite with coverage reporting"
	@echo "  lint         run black, isort, and ruff in check mode"
	@echo "  format       apply black and isort"
	@echo "  type         run the mypy type checker"
	@echo "  security     run the bandit security scanner"
	@echo "  docs         build the HTML documentation"
	@echo "  bench        run the benchmark suite"
	@echo "  build        build the source distribution and the wheel"
	@echo "  clean        remove build and cache artifacts"

install:
	$(PIP) install .

install-dev:
	$(PIP) install -e ".[dev,docs,viz]"
	pre-commit install

test:
	$(PYTHON) -m pytest tests

test-cov:
	$(PYTHON) -m pytest --cov=discretus --cov-report=term-missing --cov-report=xml tests

lint:
	$(PYTHON) -m black --check discretus tests examples benchmarks
	$(PYTHON) -m isort --check-only discretus tests examples benchmarks
	$(PYTHON) -m ruff check discretus tests examples benchmarks

format:
	$(PYTHON) -m black discretus tests examples benchmarks
	$(PYTHON) -m isort discretus tests examples benchmarks

type:
	$(PYTHON) -m mypy discretus

security:
	$(PYTHON) -m bandit -c .bandit -r discretus

docs:
	$(MAKE) -C docs html

docs-clean:
	$(MAKE) -C docs clean

bench:
	$(PYTHON) -m benchmarks

build:
	$(PYTHON) -m build

release:
	./scripts/release.sh

precommit:
	pre-commit run --all-files

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache .hypothesis htmlcov .coverage coverage.xml
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +

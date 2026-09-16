.PHONY: help install install-dev test test-all test-cov lint gate format type security docs docs-strict docs-clean stubs bench clean build release precommit

PYTHON ?= python
PIP ?= $(PYTHON) -m pip

help:
	@echo "Available targets:"
	@echo "  install      install the library"
	@echo "  install-dev  install the library with the development extra"
	@echo "  test         run the test suite"
	@echo "  test-all     run every test stage the pipeline runs"
	@echo "  test-cov     run the test suite with coverage reporting"
	@echo "  lint         run black, isort, and ruff in check mode"
	@echo "  gate         run every check the pipeline runs"
	@echo "  format       apply black and isort"
	@echo "  type         run the mypy type checker"
	@echo "  security     run the bandit security scanner"
	@echo "  docs         build the HTML documentation"
	@echo "  docs-strict  build it with warnings treated as errors"
	@echo "  stubs        generate type stubs and audit the annotations"
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

# Every test stage the pipeline runs, including the docstring examples and
# the marks that a bare invocation leaves out.
test-all:
	./scripts/run_tests.sh --all

test-cov:
	$(PYTHON) -m pytest --cov=discretus --cov-report=term-missing --cov-report=xml tests

# The path list matches the one the lint workflow checks. A path checked in
# one place and not the other is a path where a defect can land.
SOURCES ?= discretus tests examples benchmarks scripts

lint:
	$(PYTHON) -m black --check $(SOURCES)
	$(PYTHON) -m isort --check-only $(SOURCES)
	$(PYTHON) -m ruff check $(SOURCES)

# Every check the pipeline runs, in the pipeline's order, through the script
# the contributing guide points at.
gate:
	./scripts/lint.sh

format:
	$(PYTHON) -m black $(SOURCES)
	$(PYTHON) -m isort $(SOURCES)

type:
	$(PYTHON) -m mypy discretus

security:
	$(PYTHON) -m bandit -c .bandit -r discretus

docs:
	$(MAKE) -C docs html

# The strict build and the page inventory, which is what the release checks.
docs-strict:
	./scripts/build_docs.sh

# Type stubs for tooling that cannot read inline annotations, and the audit
# of the annotations behind them.
stubs:
	$(PYTHON) scripts/generate_stubs.py

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

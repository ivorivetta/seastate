# Variables
include .env
export

PACKAGE_NAME := seastate
VERSION := 0.2.0

# Targets
.PHONY: install test build clean publish-test publish-prod
.PHONY: check-git-ready
.PHONY: update-stations

check-git-ready:
	@if [ -z "$$(git status | grep -E 'not staged|Untracked')" ]; then \
		echo "Git is clean"; \
	else \
		echo "Git is dirty"; \
		exit 1; \
	fi

install:
	deactivate || true
	rm -rf venv/
	python3.11 -m venv venv
	venv/bin/python -m pip install --upgrade pip
	venv/bin/python -m pip install -r requirements.txt

update-stations:
	venv/bin/python seastate/data/__init__.py
	
test:
	venv/bin/python -m pip install --upgrade pytest faker
	venv/bin/python -m pytest tests

build: clean
	sed -i '' "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml
	venv/bin/python -m pip install --upgrade build
	venv/bin/python -m build

publish-test: build
	venv/bin/python -m pip install --upgrade twine
	venv/bin/python -m twine upload --repository testpypi -u __token__ -p ${PYPI_TEST_TOKEN} dist/*

publish-prod: build check-git-ready
	git commit -m "Release ${VERSION}"
	venv/bin/python -m pip install --upgrade twine
	venv/bin/python -m twine upload -u __token__ -p ${PYPI_TOKEN} dist/*

clean:
	rm -rf build dist *.egg-info


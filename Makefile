# Variables
PACKAGE_NAME := seastate
VERSION := 0.2.0rc1

# Targets
.PHONY: install venv test build clean publish

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

publish-test:
	venv/bin/python -m pip install --upgrade twine
	venv/bin/python -m twine upload --repository testpypi -u __token__ -p ${PYPI_TEST_TOKEN} dist/*

publish-prod:
	twine upload -u __token__ -p ${PYPI_TOKEN} dist/*
clean:
	rm -rf build dist *.egg-info


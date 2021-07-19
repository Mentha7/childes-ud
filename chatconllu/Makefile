.PHONY: docs

help:
	@echo "available make commands:"
	@echo " - installchatconllu: install chatconllu"
	@echo " - install          : install all requirements"
	@echo " - docs             : generate mkdocs"

install:
	poetry install

installchatconllu:
	python -m pip install -e .

docs:
	mkdocs serve

test: tests/*
	pytest  tests/. -v

run:
	chatconllu -d . tests

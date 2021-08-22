.PHONY: docs

help:
	@echo "available make commands:"
	@echo " - installchatconllu: install chatconllu"
	@echo " - install          : install all requirements"
	@echo " - docs             : generate mkdocs"
	@echo " - test             : run all tests"
	@echo " - run              : chatconllu -d . tests"
	@echo " - runcha           : chatconllu -d . tests"
	@echo " - runconllu        : chatconllu -d . -f conllu tests"


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

runcha:
	chatconllu -d . tests -fn vioncolas_Vioncolas_09-arb-consec_11409ims

runconllu:
	chatconllu -d ./tests -f conllu fra

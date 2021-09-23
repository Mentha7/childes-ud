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

# runcha:
#   chatconllu -d ./tests collection -fn newtest

# runconllu:
#   chatconllu -d ./tests -f conllu collection -fn newtest

# runcha:
#   chatconllu -d ./tests fra

# runconllu:
#   chatconllu -d ./tests -f conllu fra

runcha:
	chatconllu -d ./tests eng

runconllu:
	chatconllu -d ./tests -f conllu eng

# validatecha:

validateconllu:
	python tests/validate.py --lang en --level 2 tests/eng/*.conllu

clearconllu:
	chatconllu -d ./tests --no-mor --no-mor --no-misc eng

emptytiers:
	chatconllu -d ./tests --new-mor --new-gra eng

addtiers:
	chatconllu -d ./tests --cnl --pos eng

seediff:
	icdiff ./tests/eng/{}

thesis:
	cd ../thesis/ba-thesis && lualatex main.tex

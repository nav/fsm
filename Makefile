SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help
help:			## Show this help
	@printf "\nUsage: make <command>\n\nThe following commands are available:\n\n"
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
	@printf "\n"

.PHONY: install
install:		## Install dependencies
	rm -rf .venv
	python3 -m venv .venv
	./.venv/bin/python -m pip install -r requirements.txt

.PHONY: test
test:			## Run tests
	./.venv/bin/python -m unittest fsm/test_fsm.py

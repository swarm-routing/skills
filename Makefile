# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# skills: the org's standard targets (swarm-routing/.github#11). Every org
# repo has these same target names, with this repo's own commands behind them;
# `org-sync check` verifies the names are present, never the recipes. Add
# repo-only targets at the end. `make help` lists everything with a `## ` note.

NS3_IMAGE ?= ghcr.io/swarm-routing/ns3-dev:latest-debug
PLATFORM  ?=
# The org tooling (check-headers.py, org-sync), cloned once on demand.
ORG_DIR   ?= $(HOME)/.cache/swarm-routing/dotgithub

.DEFAULT_GOAL := help
.PHONY: help build test lint format check clean shell ci headers org-sync-check org-tools

help: ## list the targets
	@awk 'BEGIN{FS=":.*## "} /^[a-zA-Z0-9_-]+:.*## /{printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## build what this repo ships
	@echo "make build: nothing to do in this repo (kind skills)"

test: ## the fast tests CI runs on every PR
	python3 -I tools/checks/check-plugins.py . && python3 -I tools/checks/test_check_plugins.py
	python3 -I tools/evals/grade.py --self-test

lint: ## static checks, no changes
	actionlint

format: ## apply the formatters
	@echo "make format: nothing to do in this repo (kind skills)"

clean: ## remove build outputs
	@echo "make clean: nothing to do in this repo (kind skills)"

shell: ## an interactive shell in the dev image with this repo at /src
	@command -v docker >/dev/null || { echo "make shell: docker not found (Docker Desktop, Colima, or docker.io)" >&2; exit 127; }
	docker run --rm -it -v "$(CURDIR):/src" -w /src $(if $(PLATFORM),--platform $(PLATFORM)) python:3.13-slim bash

org-tools:
	@test -d "$(ORG_DIR)/.git" || git clone -q --depth 1 https://github.com/swarm-routing/.github "$(ORG_DIR)"

headers: org-tools ## licence headers (org rule 1)
	python3 -I "$(ORG_DIR)/tools/checks/check-headers.py" --dual '' .

org-sync-check: org-tools ## org-managed files match the org templates
	python3 -I "$(ORG_DIR)/tools/org-sync/org_sync.py" check .

check: lint test headers org-sync-check ## everything CI gates on

ci: check ## exactly what CI runs

# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
#
# skills: the org's standard targets (swarm-routing/.github#11). Every org
# repo has these same target names, with this repo's own commands behind them;
# `org-sync check` verifies the names are present, never the recipes. Add
# repo-only targets at the end. `make help` lists everything with a `## ` note.

NS3_IMAGE ?= ghcr.io/swarm-routing/ns3-dev:latest-debug
PLATFORM  ?=

.DEFAULT_GOAL := help
.PHONY: help build test lint format check clean shell ci headers org-sync-check org-tools dist

help: ## list the targets
	@awk 'BEGIN{FS=":.*## "} /^[a-zA-Z0-9_-]+:.*## /{printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## build what this repo ships
	@echo "make build: nothing to do in this repo (kind skills)"

test: ## the fast tests CI runs on every PR
	python3 -I tools/checks/check-plugins.py . && python3 -I tools/checks/test_check_plugins.py
	python3 -I tools/checks/test_wrapper_cache.py
	python3 -I tools/evals/grade.py --self-test
	python3 -I tools/token-audit/token_audit.py --self-test
	python3 -I tools/tracker-responses/responses.py --self-test
	python3 -I tools/checks/test_mcp_launcher.py

lint: ## static checks, no changes
	actionlint

format: ## apply the formatters
	@echo "make format: nothing to do in this repo (kind skills)"

clean: ## remove build outputs
	@echo "make clean: nothing to do in this repo (kind skills)"

shell: ## an interactive shell in the dev image with this repo at /src
	@command -v docker >/dev/null || { echo "make shell: docker not found (Docker Desktop, Colima, or docker.io)" >&2; exit 127; }
	docker run --rm -it -v "$(CURDIR):/src" -w /src $(if $(PLATFORM),--platform $(PLATFORM)) python:3.13-slim bash

headers: org-tools ## licence headers (org rule 1)
	"$(ORG_DIR)/tools/checks/check-headers.sh" --dual '' .

check: lint test headers org-sync-check ## everything CI gates on

ci: check ## exactly what CI runs

# The release asset (swarm-routing/.github#636): the plugin tree at HEAD as
# skills-<version>.tar.gz, deterministic (git archive). reusable-release.yml's
# build runs it at the release commit with RELEASE_VERSION set, which must be
# plugin.json's version (Commitizen bumped both).
dist: ## the release asset: dist/skills-<version>.tar.gz
	@v=$$(python3 -I -c 'import json; print(json.load(open(".claude-plugin/plugin.json"))["version"])'); \
	if [ -n "$$RELEASE_VERSION" ] && [ "$$RELEASE_VERSION" != "$$v" ]; then \
	  echo "make dist: RELEASE_VERSION $$RELEASE_VERSION != plugin.json $$v" >&2; exit 1; fi; \
	mkdir -p dist && git archive --format=tar.gz --prefix="skills-$$v/" -o "dist/skills-$$v.tar.gz" HEAD && \
	echo "dist/skills-$$v.tar.gz"

# org-sync:begin org-tools
# The org tooling (check-headers, org-sync): a shallow clone, refreshed to ORG_REF,
# by default the template commit .github/org-sync.lock pins, as CI checks (#586).
ORG_DIR   ?= $(HOME)/.cache/swarm-routing/dotgithub
ORG_REF   ?= $(or $(shell sed -nE 's/^commit = "([0-9a-f]{40})"[[:space:]]*$$/\1/p' .github/org-sync.lock 2>/dev/null),main)
# make pre-push TITLE='type(scope): subject': the PR title rule of reusable-pr-title.yml
export TITLE
TITLE_RE  := ^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9._/-]+\))?!?: [^A-Z ](.*[^ ])?$$

.PHONY: org-tools org-sync-check pre-push

org-tools:  # the same templates CI checks against: refreshed to ORG_REF every time
	@[ -d "$(ORG_DIR)/.git" ] || { git init -q "$(ORG_DIR)" && git -C "$(ORG_DIR)" remote add origin https://github.com/swarm-routing/.github; }
	@git -C "$(ORG_DIR)" fetch -q --depth 1 origin $(ORG_REF) && git -C "$(ORG_DIR)" checkout -q --detach FETCH_HEAD

org-sync-check: org-tools ## org-managed files match the org templates
	python3 -I "$(ORG_DIR)/tools/org-sync/org_sync.py" check .

pre-push: check ## before every push: make check, then TITLE='type(scope): subject' (the PR title)
	@[ -n "$$TITLE" ] || { echo "make pre-push: pass TITLE='<the PR title>'" >&2; exit 2; }
	@printf '%s\n' "$$TITLE" | grep -Eq '$(TITLE_RE)' || { echo "PR title is not a lowercase Conventional Commit: $$TITLE" >&2; exit 1; }
	@echo "pre-push: ok ($$TITLE)"

.PHONY: doctor
doctor: ## this machine's tools against the versions CI runs (the org's tools/versions.env, go.mod), and the hosts the network steps need
	@$(MAKE) -s org-tools || echo "doctor: could not refresh $(ORG_DIR) (offline?): using it as it is" >&2
	@"$(ORG_DIR)/tools/doctor/doctor.sh" .

# ruff as reusable-python-ci.yml runs it (#997): the repository's own ruff config,
# else the org ruff.toml (from ORG_DIR); `ruff-setup` refreshes ORG_DIR and warns
# when the local ruff is not the org's RUFF_VERSION (tools/versions.env)
RUFF_CONFIG = $(if $(wildcard ruff.toml .ruff.toml)$(shell grep -qs '^\[tool\.ruff' pyproject.toml && echo own),,--config "$(ORG_DIR)/ruff.toml")
.PHONY: ruff-setup
ruff-setup:
	@$(MAKE) -s org-tools || echo "ruff-setup: could not refresh $(ORG_DIR) (offline?): using it as it is" >&2
	@want=$$(sed -n 's/^RUFF_VERSION=//p' "$(ORG_DIR)/tools/versions.env"); have=$$(ruff --version 2>/dev/null | cut -d' ' -f2); \
	  [ "$$have" = "$$want" ] || echo "ruff-setup: ruff $${have:-not found}, CI runs $$want: pip install ruff==$$want" >&2
# org-sync:end org-tools

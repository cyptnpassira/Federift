# federift — build/run helpers. stdlib-only project, so no dependency install.
PY      ?= python
SCEN    ?= federift/scenarios/fractured-robust.json
TRACE   ?= trace.json

.PHONY: build build-go build-py run pipeline partition privacy clean help

help:
	@echo "targets: build build-go build-py run pipeline partition privacy clean"

build: build-go build-py ## compile both halves

build-go: ## go build + vet

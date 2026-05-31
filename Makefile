# federift — build/run helpers. stdlib-only project, so no dependency install.
PY      ?= python
SCEN    ?= federift/scenarios/fractured-robust.json
TRACE   ?= trace.json

.PHONY: build build-go build-py run pipeline partition privacy clean help

help:
	@echo "targets: build build-go build-py run pipeline partition privacy clean"

build: build-go build-py ## compile both halves

build-go: ## go build + vet
	cd topology && go build ./... && go vet ./...

build-py: ## python bytecode-compile check
	$(PY) -m compileall -q federift

run: ## run a scenario through the Python core (no network trace)
	$(PY) -m federift run $(SCEN)

partition: ## show non-IID label skew for a scenario
	$(PY) -m federift partition $(SCEN)

privacy: ## print the DP accounting approximation
	$(PY) -m federift privacy $(SCEN)

pipeline: ## Go emits a network trace, Python consumes it
	cd topology && go run ./cmd/topology -scenario ../$(SCEN) -emit-trace ../$(TRACE)
	$(PY) -m federift run $(SCEN) --trace $(TRACE)

clean: ## remove build artifacts and traces
	-cd topology && go clean ./...
	-$(PY) -c "import shutil,glob,os; [shutil.rmtree(p,ignore_errors=True) for p in glob.glob('federift/**/__pycache__',recursive=True)]"
	-$(PY) -c "import os; os.path.exists('$(TRACE)') and os.remove('$(TRACE)')"

# draft note 72

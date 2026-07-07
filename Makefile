# Get the currently used golang install path (in GOPATH/bin, unless GOBIN is set)
ifeq (,$(shell go env GOBIN))
GOBIN=$(shell go env GOPATH)/bin
else
GOBIN=$(shell go env GOBIN)
endif

# Project metadata and build settings.
BINARY  := falcon-mcp
MODULE  := github.com/crowdstrike/falcon-mcp
MAIN    := ./cmd/falcon-mcp/main.go
DIST    := dist
# VERSION stamps the assembled npm/python packages (the build binary is unstamped).
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo 0.0.0+dev)

# npm platform tuples: <uname-os>:<uname-arch>:<npm-os>:<npm-cpu>:<goos>:<goarch>.
# The sub-package name uses uname arch (matching what npm/falcon-mcp/bin/index.js resolves);
# os/cpu use npm's values so npm installs only the matching optional dependency;
# goos/goarch locate the binary in goreleaser's per-target build directory.
NPM_PLATFORMS := macos:x86_64:darwin:x64:darwin:amd64 macos:arm64:darwin:arm64:darwin:arm64 linux:x86_64:linux:x64:linux:amd64 linux:arm64:linux:arm64:linux:arm64 windows:x86_64:win32:x64:windows:amd64 windows:arm64:win32:arm64:windows:arm64

.PHONY: all
all: build

##@ General

# The help target prints out all targets with their descriptions organized
# beneath their categories. The categories are represented by '##@' and the
# target descriptions by '##'. The awk command is responsible for reading the
# entire set of makefiles included in this invocation, looking for lines of the
# file as xyz: ## something, and then pretty-format the target and help. Then,
# if there's a line with ##@ something, that gets pretty-printed as a category.
# More info on the usage of ANSI control characters for terminal formatting:
# https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_parameters
# More info on the awk command:
# http://linuxcommand.org/lc3_adv_awk.php

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.PHONY: fmt
fmt: ## Run go fmt against code.
	go fmt ./...

.PHONY: vet
vet: ## Run go vet against code.
	go vet ./...

.PHONY: generate
generate: ## Run go generate (regenerate module aggregator and embedded FQL guide).
	go generate ./...

.PHONY: test
test: fmt vet ## Run tests with the race detector and coverage.
	go test -race ./... -coverprofile cover.out

.PHONY: license
license: addlicense ## Run addlicense to add license headers to source code.
	$(ADDLICENSE) -c 'CrowdStrike, Inc.' -skip yaml -skip yml -skip ini -skip json -skip hcl -skip toml -s -f LICENSE $(shell pwd)

.PHONY: lint
lint: golangci-lint ## Run golangci-lint linter.
	$(GOLANGCI_LINT) run ./...

.PHONY: lint-fix
lint-fix: golangci-lint ## Run golangci-lint linter and perform fixes.
	$(GOLANGCI_LINT) run --fix

##@ Build

.PHONY: build
build: fmt vet ## Build the falcon-mcp binary for the host platform.
	go build -trimpath -o $(BINARY) $(MAIN)

.PHONY: run
run: fmt vet ## Run falcon-mcp from your system.
	go run $(MAIN)

.PHONY: clean
clean: ## Remove build, packaging, and tool artifacts.
	rm -rf $(BINARY) $(DIST) cover.out bin/ npm/$(BINARY)-*/ npm/$(BINARY)/package.json

##@ Packaging

.PHONY: snapshot
snapshot: goreleaser ## Build unpublished per-platform binaries into dist/ via goreleaser.
	$(GORELEASER) release --snapshot --clean

.PHONY: npm-assemble
npm-assemble: snapshot ## Assemble npm platform sub-packages and render the main package.json.
	@set -e; \
	for p in $(NPM_PLATFORMS); do \
	  IFS=: read -r os arch npmos npmcpu goos goarch <<< "$$p"; \
	  suffix=""; if [ "$$os" = "windows" ]; then suffix=".exe"; fi; \
	  pkg="$(BINARY)-$$os-$$arch"; \
	  dir=$$(find $(DIST) -maxdepth 1 -type d -name "*_$${goos}_$${goarch}*" | head -n1); \
	  src=$$(find "$$dir" -maxdepth 1 -type f | head -n1); \
	  if [ -z "$$dir" ] || [ -z "$$src" ]; then echo "missing binary for $$goos/$$goarch in $(DIST)/"; exit 1; fi; \
	  mkdir -p "npm/$$pkg/bin"; \
	  cp "$$src" "npm/$$pkg/bin/$$pkg$$suffix"; \
	  printf '{\n  "name": "%s",\n  "version": "%s",\n  "os": ["%s"],\n  "cpu": ["%s"]\n}\n' \
	    "$$pkg" "$(VERSION)" "$$npmos" "$$npmcpu" > "npm/$$pkg/package.json"; \
	  echo "assembled npm/$$pkg"; \
	done; \
	sed 's/__VERSION__/$(VERSION)/g' npm/$(BINARY)/package.json.tmpl > npm/$(BINARY)/package.json; \
	node --check npm/$(BINARY)/bin/index.js; \
	echo "rendered npm/$(BINARY)/package.json (version $(VERSION))"

.PHONY: python-build
python-build: ## Build the Python wheel/sdist (pure-python wrapper; version stays 0.0.0 locally).
	cd python && uv build

##@ Dependencies

## Location to install dependencies to
LOCALBIN ?= $(shell pwd)/bin
$(LOCALBIN):
	mkdir -p $(LOCALBIN)

## Tool Binaries
GOLANGCI_LINT = $(LOCALBIN)/golangci-lint
ADDLICENSE = $(LOCALBIN)/addlicense
GORELEASER = $(LOCALBIN)/goreleaser

## Tool Versions
GOLANGCI_LINT_VERSION ?= v2.11.3
ADDLICENSE_VERSION ?= latest
GORELEASER_VERSION ?= latest

.PHONY: golangci-lint
golangci-lint: $(GOLANGCI_LINT) ## Download golangci-lint locally if necessary.
$(GOLANGCI_LINT): $(LOCALBIN)
	$(call go-install-tool,$(GOLANGCI_LINT),github.com/golangci/golangci-lint/v2/cmd/golangci-lint,$(GOLANGCI_LINT_VERSION))

.PHONY: addlicense
addlicense: $(ADDLICENSE) ## Download addlicense locally if necessary.
$(ADDLICENSE): $(LOCALBIN)
	$(call go-install-tool,$(ADDLICENSE),github.com/google/addlicense,$(ADDLICENSE_VERSION))

.PHONY: goreleaser
goreleaser: $(GORELEASER) ## Download goreleaser locally if necessary.
$(GORELEASER): $(LOCALBIN)
	$(call go-install-tool,$(GORELEASER),github.com/goreleaser/goreleaser/v2,$(GORELEASER_VERSION))

# go-install-tool will 'go install' any package with custom target and name of binary, if it doesn't exist
# $1 - target path with name of binary
# $2 - package url which can be installed
# $3 - specific version of package
define go-install-tool
@[ -f "$(1)-$(3)" ] || { \
set -e; \
package=$(2)@$(3) ;\
echo "Downloading $${package}" ;\
rm -f $(1) || true ;\
GOBIN=$(LOCALBIN) go install $${package} ;\
mv $(1) $(1)-$(3) ;\
} ;\
ln -sf $(1)-$(3) $(1)
endef

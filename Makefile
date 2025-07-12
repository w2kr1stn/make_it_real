IMAGE=make-it-real
IDEA?=task management app for developers

all: help

##@ Development

container: ## Build container image.
	docker build --rm -t $(IMAGE) .

run: container ## Run container.
	docker run --rm -ti --network=host --env-file=.env $(IMAGE) "$(IDEA)"

compose-up: container ## Run the compose project.
	docker compose up -d
	docker compose exec make-it-real uv run makeitreal "$(IDEA)"


##@ General

help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

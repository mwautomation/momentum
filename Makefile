COMPOSE ?= docker compose
TEST_COMPOSE = $(COMPOSE) -f compose.yaml -f compose.test.yaml --project-name library-api-test

.PHONY: up down logs ps test

up:
	$(COMPOSE) up --build --detach

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs --follow api

ps:
	$(COMPOSE) ps

test:
	@set -eu; \
	trap '$(TEST_COMPOSE) down --volumes --remove-orphans' EXIT; \
	$(TEST_COMPOSE) up --build --abort-on-container-exit \
		--exit-code-from tests tests

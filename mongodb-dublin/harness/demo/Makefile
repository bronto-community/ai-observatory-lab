# The Storefront incident on MongoDB Atlas.
#   make up        first start: seed the database, build the good release, start everything
#   make release   ship v4.1.0 (the slow checkout)
#   make rollback  back to v4.0.0
SF = ../storefront

up: seed rollback
	docker compose up -d psp loadgen collector caddy

seed:
	docker run --rm --env-file .env -v $(CURDIR)/seed.py:/seed.py:ro -v $(abspath $(SF))/scripts:/scripts:ro python:3.12-slim \
	  sh -c "pip install -q pymongo==4.15.1 && python /seed.py && python /scripts/create_indexes.py"

release: TAG = v4.1.0
rollback: TAG = v4.0.0
release rollback:
	git -C $(SF) checkout -q $(TAG)
	GIT_COMMIT=$$(git -C $(SF) rev-parse HEAD) SERVICE_VERSION=$(TAG:v%=%) \
	  docker compose up -d --build web catalog checkout payments
	@echo "$(TAG) is live"

down:
	docker compose down

.PHONY: up seed release rollback down

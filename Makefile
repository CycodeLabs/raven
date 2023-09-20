
setup:
	@echo "Building Services..."
	docker-compose --file deployment/docker-compose.yml up -d

test:
	@echo "Running Tests..."
	@pytest -v tests/
	@python test_raven.py
setup:
	@echo "Building Services..."
	docker-compose -p raven --file deployment/docker-compose.yml up -d

test-build:
	@echo "Running Tests in isolated environment..."
	docker-compose -p test-raven --file deployment/test.docker-compose.yml up --force-recreate --build --abort-on-container-exit

test-run:
	@echo "DO NOT USE DIRECTLY; PLEASE USE: make test-build"
	@echo "Running Tests..."
	@python3 test_raven.py
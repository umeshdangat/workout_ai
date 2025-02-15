.PHONY: setup start stop clean

setup:
	@echo "Setting up local dev environment..."
	docker-compose up -d

start:
	@echo "Starting services..."
	docker-compose start

stop:
	@echo "Stopping services..."
	docker-compose stop

clean:
	@echo "Removing all services and data..."
	docker-compose down -v

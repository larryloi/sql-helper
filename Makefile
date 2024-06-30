include Makefile.env

build:
	docker build -t $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) .

### the config.yml path may need to change for test
run:
	docker run --rm -it -v ./mssql_inventory/config.yml:/app/config.yml -v ./mssql_inventory/orders_demo00_creator.py:/app/mssql_inventory/orders_demo00_creator.py $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) /bin/bash

run1:
	docker run --rm -it -v ./mssql_inventory/config.yml:/app/config.yml -v ./mssql_inventory/orders_creator.py:/app/mssql_inventory/orders_creator.py $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) /bin/bash
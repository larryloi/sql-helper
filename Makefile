include Makefile.env

build:
	docker build -t $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) .

### the config.yml path may need to change for test
run:
	docker run --rm -it -v ./$(APP_DB)/config.yml:/app/config.yml -v ./$(APP_DB)/orders_demo00_creator.py:/app/$(APP_DB)/orders_demo00_creator.py $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) /bin/bash

run1:
	docker run --rm -it -v ./$(APP_DB)/config.yml:/app/config.yml -v ./$(APP_DB)/$(APP_TBL).py:/app/$(APP_DB)/$(APP_TBL).py $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) /bin/bash
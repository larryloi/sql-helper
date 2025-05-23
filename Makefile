include Makefile.env

build.base:
	docker build -t $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(BASE_NAME):$(BASE_VER) --target base .

build.app:
	docker build -t $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) --target app .

push.app:
	docker push $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) 

### the config.yml path may need to change for test
#run:
#	docker run --rm -it -v ./$(APP_DB)/config.yml:/app/config.yml -v ./$(APP_DB)/orders_creator.py:/app/$(APP_DB)/orders_creator.py $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) /bin/bash

run.mount:
	docker run --rm -it -v ./common/:/app/common/ -v ./$(APP_DB)/config.yml:/app/config.yml -v ./$(APP_DB)/:/app/$(APP_DB)/ $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) /bin/bash

run:
	docker run --rm -it $(IMAGE_REPO_ROOT)/$(PROJECT_NAME)-$(APP_NAME):$(APP_VER) /bin/bash

up: 
	docker compose --profile $(db) up -d

down:
	docker compose --profile $(db) down

logs:
	docker compose --profile $(db) logs -f

ps:
	docker compose --profile $(db) ps
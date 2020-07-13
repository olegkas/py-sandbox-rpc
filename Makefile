.PHONY: help venv init build compose logs run cleanup ls-dangling rm-dangling demo

default: help

service:=sample-rpc-service
tag:=latest

help:
	@echo make venv
	@echo "  - Creates virtual environment in project folder 'venv'"
	@echo
	@echo make init
	@echo "  - Upgrades pip, installs project and test requirements into project virual environment"
	@echo
	@echo make down
	@echo "  - Shuts down docker container"
	@echo
	@echo make build
	@echo "  - Builds docker image using project Dockerfile"
	@echo
	@echo make compose:
	@echo "  - Shuts down, rebuilds and starts project as docker container"
	@echo
	@echo make logs:
	@echo "  - Shows project container logs with --follow flag"
	@echo
	@echo make run:
	@echo "  - Runs docker build image, compose and logs in one command"
	@echo
	@echo make demo:
	@echo "  - Starts rpc service in a container and runs scripts with rpc"
	@echo
	@echo make cleanup:
	@echo "  - Stops project container, removes container and image, deletes untagged images"
	@echo
	@echo make ls-dangling:
	@echo "  - Lists all dangling (untagged) images"
	@echo
	@echo make rm-dangling:
	@echo "  - Removes all dangling (untagged) images"
	@echo

init:
	@set -e
	source ./venv/bin/activate
	python -m pip install --upgrade pip
	python -m pip install --upgrade setuptools wheel
	python -m pip install -r requirements.txt;

venv:
	@set -e
	python3 -m venv venv
	make init

server_down:
	@set -e
	docker-compose -f "demo/docker-compose.yml" down

server_build:
	@set -e
	make server_down
	docker build --rm -f "demo/Dockerfile" -t $(service):$(tag) .

server_compose:
	@set -e
	docker-compose -f "demo/docker-compose.yml" down
	docker-compose -f "demo/docker-compose.yml" up -d --build

server_logs:
	docker logs -f $(service)

server_run:
	@set -e
	make server_build
	docker-compose -f "demo/docker-compose.yml" up -d --build
	make server_logs

cleanup_pkg:
	@set -e
	@echo ">>>>>>>>>>>>>>>>>>>> REMOVE PACAGE <<<<<<<<<<<<<<<<<<<<<<<<"
	- rm demo/easy_pyrpc-*.whl
	pip uninstall -y easy_pyrpc
	@echo ">>>>>>>>>>>>>>>>>>>> REMOVE PACAGE DONE<<<<<<<<<<<<<<<<<<<<<<<<"

prepare_service:
	@set -e
	@echo ">>>>>>>>>>>>>>>>>>>> BUILD RPC PACKAGE  <<<<<<<<<<<<<<<<<<<<<<<<"
	python ./setup.py bdist_wheel
	cp ./dist/easy_pyrpc-*.whl ./demo
	@echo ">>>>>>>>>>>>>>>>>>>> START CONTAINER RPC BACKEND <<<<<<<<<<<<<<<<<<<<<<<<"
	make server_build
	make server_compose
	@echo ">>>>>>>>>>>>>>>>>>>> PREPARE SERVICE DONE <<<<<<<<<<<<<<<<<<<<<<<<"

prepare_client:
	@set -e
	@echo ">>>>>>>>>>>>>>>>>>>> (RE)INSTALL RPC PACKAGE TO USE LOCALY  <<<<<<<<<<<<<<<<<<<<<<<<"
	pip uninstall -y easy_pyrpc
	pip install demo/easy_pyrpc-*.whl
	@echo ">>>>>>>>>>>>>>>>>>>> PREPARE CLIENT DONE <<<<<<<<<<<<<<<<<<<<<<<<"

demo_run:
	@set -e
	@echo ">>>>>>>>>>>>>>>>>>>> RUN LOCAL PYTHON SCRIPTS WITH RPCS <<<<<<<<<<<<<<<<<<<<<<<<"
	python demo/sample_rpc_client.py
	@echo ">>>>>>>>>>>>>>>>>>>> HERE IT SHOWS RPC SERVICE CONTAINER LOGS <<<<<<<<<<<<<<<<<<<<<<<<"
	docker logs $(service)
	@echo ">>>>>>>>>>>>>>>>>>>> DEMO RUN DONE, CHECK OUTPUT ABOVE <<<<<<<<<<<<<<<<<<<<<<<<"

demo:
	@set -e
	make prepare_service
	make prepare_client
	make demo_run

ls-dangling:
	docker images -f dangling=true

rm-dangling:
    docker images -f dangling=true -q | xargs docker rmi

cleanup_container:
	@set -e
	@echo ">>>>>>>>>>>>>>>>>>>> REMOVE CONTAINER <<<<<<<<<<<<<<<<<<<<<<<<"
	make server_down
	- docker rm -f $(service)
	- docker rmi -f $(service):$(tag)
	- make rm-dangling
	docker ps
	@echo ">>>>>>>>>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<<<<<<<<<<"

cleanup:
	@set -e
	make cleanup_pkg
	make cleanup_container
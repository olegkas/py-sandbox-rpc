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
	source ./venv/bin/activate;
	python -m pip install --upgrade pip;
	python -m pip install -r requirements.txt;

venv:
	@set -e
	python3 -m venv venv
	make init

down:
	@set -e
	docker-compose -f "demo/docker-compose.yml" down

build:
	@set -e
	make down
	docker build --rm -f "demo/Dockerfile" -t $(service):$(tag) .

compose:
	@set -e
	docker-compose -f "demo/docker-compose.yml" down
	docker-compose -f "demo/docker-compose.yml" up -d --build

logs:
	docker logs -f $(service)

run:
	@set -e
	make build
	docker-compose -f "demo/docker-compose.yml" up -d --build
	make logs

demo:
	@set -e
	@echo ">>>>>>>>>>>>>>>>>>>> HERE IT BUILDS PACKAGE  <<<<<<<<<<<<<<<<<<<<<<<<"
	- rm demo/sandbox_rpc-*.whl
	pip uninstall -y sandbox_rpc
	python ./setup.py bdist_wheel
	cp ./dist/sandbox_rpc-*.whl ./demo
	@echo ">>>>>>>>>>>>>>>>>>>> HERE IT BUILDS & STARTS RPC SERVICE CONTAINER <<<<<<<<<<<<<<<<<<<<<<<<"
	make build
	make compose
	@echo ">>>>>>>>>>>>>>>>>>>> HERE IT RUNS LOCAL SCRIPTS WITH RPCS  <<<<<<<<<<<<<<<<<<<<<<<<"
	pip install demo/sandbox_rpc-*.whl
	@echo ">>>>>>>>>>>>>>>>>>>> HERE IT RUNS LOCAL SCRIPTS WITH RPCS  <<<<<<<<<<<<<<<<<<<<<<<<"
	python demo/sample_rpc_client.py
	@echo ">>>>>>>>>>>>>>>>>>>> HERE IT SHOWS RPC SERVICE CONTAINER LOGS <<<<<<<<<<<<<<<<<<<<<<<<"
	docker logs $(service)
	@echo ">>>>>>>>>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<<<<<<<<<<"

ls-dangling:
	docker images -f dangling=true

rm-dangling:
	docker images -f dangling=true -q | xargs docker rmi

cleanup:
	@set -e
	@echo ">>>>>>>>>>>>>>>>>>>> REMOVE PACAGE <<<<<<<<<<<<<<<<<<<<<<<<"
	- rm demo/sandbox_rpc-*.whl
	pip uninstall -y sandbox_rpc
	@echo ">>>>>>>>>>>>>>>>>>>> REMOVE CONTAINER <<<<<<<<<<<<<<<<<<<<<<<<"
	make down
	- docker rm -f $(service)
	- docker rmi -f $(service):$(tag)
	- make rm-dangling
	docker ps
	@echo ">>>>>>>>>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<<<<<<<<<<"
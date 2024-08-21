.PHONY: ensure-docker install-docker-mac install-docker-linux install-docker-wsl2 setup build run stop restart check-docker-status setup-profile deploy-lambda create-sns-topic count-messages deploy-resources clean

.ONESHELL:

export BASE_PATH ?= $(shell pwd)
export LAMBDA_FILE_DIRECTORY ?= ./src/part-2/solution/
export LAMBDA_FILE_NAME ?= event_processor.py
export ZIP_FILE ?= function.zip
export AWS_PROFILE ?= localstack
export AWS_ENDPOINT_URL ?= http://localhost:4566
export AWS_REGION ?= eu-west-1
export LAMBDA_ROLE_ARN ?= arn:aws:iam::000000000000:role/lambda-role


export LAMBDA_FUNCTION_NAME ?= TestLambda
export SNS_TOPIC_NAME ?= FlightNotifications


# Detect OS
OS := $(shell uname)

ensure-docker:
	@which docker > /dev/null; \
	if [ $$? -ne 0 ]; then \
		$(MAKE) install-docker; \
	else \
		echo "Docker is already installed."; \
	fi

install-docker:
ifeq ($(OS), Darwin)
	$(MAKE) install-docker-mac
else ifeq ($(OS), Linux)
	$(MAKE) install-docker-linux
else
	$(MAKE) install-docker-wsl2
endif

################## Install targets #########################
install-docker-mac:
	@echo "Installing Docker on macOS..."
	@brew install docker docker-compose
	@echo "Docker installed successfully on macOS."

install-docker-linux:
	@echo "Installing Docker on Linux..."
	@sudo apt-get update
	@sudo apt-get install -y docker.io docker-compose
	@sudo systemctl start docker
	@sudo systemctl enable docker
	@sudo usermod -aG docker $$USER
	@echo "Docker installed successfully on Linux."

install-docker-wsl2:
	@echo "Setting up Docker on Windows with WSL2..."
	@powershell -Command "wsl --install"
	@wsl --set-default-version 2
	@wsl --install -d Ubuntu
	@wsl -d Ubuntu -- bash -c 'sudo apt-get update && sudo apt-get install -y docker.io docker-compose && sudo usermod -aG docker $$(whoami)'
	@echo "Docker installed successfully on Windows with WSL2. Please restart your terminal."

setup: ensure-docker

build:
	@echo "Building Docker images..."
	@docker-compose -f docker-compose.yml build

run:
	@echo "Running Docker Compose..."
	@docker-compose -f ./infra/docker-compose.yml up

stop:
	@echo "Stopping Docker Compose..."
	@docker-compose -f ./infra/docker-compose.yml down

restart:
	@echo "Restarting Docker Compose services..."
	@docker-compose -f ./infra/docker-compose.yml down
	@docker-compose -f ./infra/docker-compose.yml up

check-docker-status:
	@echo "Checking Docker status..."
	@docker --version
	@docker-compose --version

setup-profile:
	@echo "Configuring LocalStack AWS CLI profile..."
	aws configure set aws_access_key_id dummy --profile $(AWS_PROFILE)
	aws configure set aws_secret_access_key dummy --profile $(AWS_PROFILE)
	aws configure set region $(AWS_REGION) --profile $(AWS_PROFILE)
	@echo "LocalStack profile configured."

################## Application targets #########################
deploy-lambda: setup-profile
	@echo "Packaging Lambda function..."
	cp $(LAMBDA_FILE_DIRECTORY)/$(LAMBDA_FILE_NAME) .
	zip $(ZIP_FILE) $(LAMBDA_FILE_NAME)
	rm -rf $(LAMBDA_FILE_NAME)

	@echo "Deploying Lambda function..."
	aws --endpoint-url=$(AWS_ENDPOINT_URL) lambda create-function \
		--function-name $(LAMBDA_FUNCTION_NAME) \
		--runtime python3.8 \
		--handler event_processor.lambda_handler \
		--zip-file fileb://$(ZIP_FILE) \
		--role $(LAMBDA_ROLE_ARN) \
		--no-cli-pager \
		--timeout 30

	@echo "Lambda function deployed."


create-sns-topic:
	@echo "Creating SNS topic..."
	aws --endpoint-url=$(AWS_ENDPOINT_URL) sns create-topic \
		--no-cli-pager \
		--name $(SNS_TOPIC_NAME)
	@echo "SNS topic created."

count-messages:
	@echo "Counting messages in SNS: $(SNS_TOPIC_NAME)"
	@MINS=$(mins); \
	if [ -z "$$NUMBER" ]; then \
	    MINS=1; \
	fi; \
	PERIOD=$$((MINS * 60)); \
	TODAY=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	START_TIME=$$(date -u -v-1d +"%Y-%m-%dT%H:%M:%SZ"); \
	END_TIME=$$TODAY; \
	aws --endpoint-url=$(AWS_ENDPOINT_URL) cloudwatch get-metric-statistics \
	    --namespace "Custom/SNS" \
	    --metric-name "NumberOfMessagesPublished" \
	    --dimensions Name=TopicName,Value=$(SNS_TOPIC_NAME) \
	    --start-time $$START_TIME \
	    --end-time $$END_TIME \
	    --period $$PERIOD \
	    --statistics Sum \
	    --no-cli-pager \
	    --region eu-west-1


deploy-resources:
	@echo "Deploying lambda into AWS"
	make deploy-lambda
	@sleep 2

	@echo "Creating SNS topic"
	make create-sns-topic
	@sleep 2


clean:
	@echo "Cleaning up..."
	rm -f $(ZIP_FILE) output.txt
	@echo "Cleanup done."


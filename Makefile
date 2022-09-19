SHELL = /usr/bin/env bash -xeuo pipefail

stack_name:=project-artemis-library-cloud

isort:
	poetry run isort src/ tests/

black:
	poetry run black src/ tests/

format: isort black

install:
	poetry install

mypy:
	poetry run mypy src

ipython:
	PYTHONPATH=src \
	poetry run ipython

test-unit:
	PYTHONPATH=src \
	AWS_ACCESS_KEY_ID=dummy \
	AWS_SECRET_ACCESS_KEY=dummy \
	AWS_DEFAULT_REGION=ap-northeast-1 \
		poetry run python -m pytest -vv --cov=src --cov-branch tests/unit

build:
	pip install \
		feedparser==6.0.10 \
		beautifulsoup4==4.11.1 \
		boto3-stubs[dynamodb,s3,sqs]==1.24.75 \
		-t layer/python

package:
	sam package \
		--s3-bucket ${ARTIFACT_BUCKET} \
		--s3-prefix project-artemis-cloud \
		--template-file sam.yml \
		--output-template-file template.yml

deploy:
	sam deploy \
		--stack-name $(stack_name) \
		--template-file template.yml \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset

dry-deploy:
	sam deploy \
		--stack-name $(stack_name) \
		--template-file template.yml \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--no-execute-changeset \
		--no-fail-on-empty-changeset

describe:
	aws cloudformation describe-stacks \
		--stack-name $(stack_name) \
		--query Stacks[0].Outputs

localstack-up:
	docker-compose up -d

localstack-down:
	docker-compose down

.PHONY: \
	install \
	test-unit \
	build \
	package \
	deploy \
	dry-deploy \
	describe \
	localstack-up \
	localstack-down


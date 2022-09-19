SHELL = /usr/bin/env bash -xeuo pipefail

stack_name:=project-artemis-library-cloud

install:
	poetry install

build:
	pip install \
		feedparser==6.0.10 \
		beautifulsoup4==4.11.1 \
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

describe:
	aws cloudformation describe-stacks \
		--stack-name $(stack_name) \
		--query Stacks[0].Outputs

.PHONY: \
	deploy \
	describe


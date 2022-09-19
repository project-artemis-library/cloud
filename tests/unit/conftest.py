import json
from pathlib import Path
from typing import Dict, Optional

import boto3
import pytest
from boto3.resources.base import ServiceResource
from mypy_boto3_dynamodb import DynamoDBServiceResource


@pytest.fixture(scope="session")
def dynamodb_resource() -> DynamoDBServiceResource:
    return boto3.resource("dynamodb", endpoint_url="http://localhost:4566")


@pytest.fixture(scope="function")
def dynamodb(
    request, dynamodb_resource: DynamoDBServiceResource
) -> DynamoDBServiceResource:
    param: Dict[str, Optional[str]] = request.param

    base_path = str(Path(__file__).parent.joinpath("fixtures/dynamodb").resolve())

    for name_table, name_item in param.items():
        with open(f"{base_path}/{name_table}/definition.json") as f:
            definition = json.load(f)
        dynamodb_resource.create_table(**definition)
        if name_item is not None:
            with dynamodb_resource.Table(name_table).batch_writer() as batch:
                with open(f"{base_path}/{name_table}/items/{name_item}.json") as f:
                    for item in json.load(f):
                        batch.put_item(item)

    yield dynamodb_resource

    for name_table in param.keys():
        dynamodb_resource.Table(name_table).delete()

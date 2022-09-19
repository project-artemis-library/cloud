from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import List, Optional

from boto3.dynamodb.conditions import Key
from mypy_boto3_dynamodb.service_resource import Table

from logger import MyLogger
from utils.datetime import now

logger = MyLogger(__name__)


class StateArticle(str, Enum):
    Inserted = "inserted"
    Informed = "informed"


@dataclass()
class ParsedArticleData:
    title: str
    title_ja: Optional[str]
    category: str
    thumbnail: str


@dataclass()
class Article:
    url: str
    status: StateArticle
    created_at: str = field(default="")
    updated_at: str = field(default="")
    error_messages: List[Optional[str]] = field(default_factory=list)
    title: Optional[str] = field(default=None)
    title_ja: Optional[str] = field(default=None)
    category: Optional[str] = field(default=None)
    thumbnail: Optional[str] = field(default=None)

    def __post_init__(self):
        txt_now = str(now())
        if self.created_at == "":
            self.created_at = txt_now
        if self.updated_at == "":
            self.updated_at = txt_now

    def __hash__(self):
        return hash(json.dumps(asdict(self)))

    @staticmethod
    @logger.logging_function()
    def create_inserted_item(url: str) -> Article:
        return Article(
            url=url,
            status=StateArticle.Inserted,
        )

    @logger.logging_function(write_log=True)
    def append_error_message(self, message: str):
        self.updated_at = str(now())
        self.error_messages.append(message)
        logger.add_functional_data("updated", self)

    @logger.logging_function()
    def get_error_count(self) -> int:
        return len(self.error_messages)

    @logger.logging_function(write_log=True)
    def update_to_informed(self, data: ParsedArticleData):
        self.status = StateArticle.Informed
        self.updated_at = str(now())
        self.error_messages = []
        self.title = data.title
        self.title_ja = data.title_ja
        self.category = data.category
        self.thumbnail = data.thumbnail

        logger.add_functional_data("updated", self)

    @logger.logging_function(write_log=True)
    def put_item(self, table: Table):
        table.put_item(Item=asdict(self))

    @staticmethod
    @logger.logging_function(write_log=True, with_return=True, with_arg=True)
    def get_item(url: str, table: Table) -> Article:
        resp = table.get_item(Key={"url": url})
        item: dict = resp["Item"]
        return Article(**item)

    @staticmethod
    @logger.logging_function(write_log=True, with_arg=True)
    def query(status: StateArticle, table: Table) -> List[Article]:
        result: List[dict] = []

        token = None
        is_first = True
        while token is not None or is_first:
            if is_first:
                is_first = False
            option: dict = {
                "IndexName": "status-index",
                "KeyConditionExpression": Key("status").eq(status),
            }
            if token is not None:
                option["ExclusiveStartKey"] = token
            resp = table.query(**option)
            result += resp.get("Items", [])
            token = resp.get("LastEvaluatedKey")

        return [Article(**x) for x in result]

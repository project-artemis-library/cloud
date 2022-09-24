import os
from dataclasses import dataclass
from typing import Iterator, List, Optional

import boto3
import feedparser
from boto3.dynamodb.conditions import Attr
from botocore.client import ClientError
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table

from logger import MyLogger
from models.article import Article


@dataclass(frozen=True)
class EnvironmentVariables:
    dynamodb_table_name: str


@dataclass(frozen=True)
class EntrySummary:
    link: str
    title: str
    summary: Optional[str]


logger = MyLogger(__name__)

FEED_URL = "https://xml.e-hentai.org/ehg.xml"
TARGET_CATEGORY = ["Manga", "Artist CG", "Doujinshi"]


@logger.logging_handler(with_return=False)
def handler(event, context):
    main()


@logger.logging_function()
def main(dynamodb_resource: DynamoDBServiceResource = boto3.resource("dynamodb")):
    env = load_environment()
    table = dynamodb_resource.Table(env.dynamodb_table_name)
    for entry in get_feed_entries():
        if not is_target_category(entry.title):
            continue
        if has_foreigner_language_tag(entry.summary):
            continue
        insert_article(entry.link, table)


@logger.logging_function()
def load_environment() -> EnvironmentVariables:
    return EnvironmentVariables(
        **{
            k: os.environ[k.upper()]
            for k in EnvironmentVariables.__dict__["__dataclass_fields__"].keys()
        }
    )


@logger.logging_function()
def get_feed_entries() -> Iterator[EntrySummary]:
    for x in feedparser.parse(FEED_URL)["entries"]:
        yield EntrySummary(link=x["link"], title=x["title"], summary=x["summary"])


@logger.logging_function()
def is_target_category(title: str) -> bool:
    index = title.find("]")
    category = title[1:index]
    return category in TARGET_CATEGORY


@logger.logging_function()
def has_foreigner_language_tag(summary: str) -> bool:
    lower_summary = summary.lower()
    if "language" not in lower_summary:
        return False
    return "japanese" not in lower_summary


@logger.logging_function()
def insert_article(url: str, table: Table):
    article = Article.create_inserted_item(url)
    try:
        article.put_item(table, Attr("url").not_exists())
    except ClientError as e:
        if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise

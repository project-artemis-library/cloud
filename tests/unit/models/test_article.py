from typing import List

import pytest
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from freezegun import freeze_time
from mypy_boto3_dynamodb import DynamoDBServiceResource

from models.article import Article, ParsedArticleData, StateArticle


class TestArticleCreateInsertedItem:
    @pytest.mark.parametrize(
        "url, expected",
        [
            (
                "1223334444",
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                ),
            )
        ],
    )
    @freeze_time("2022-01-09 16:17:22.123456+09:00")
    def test_normal(self, url, expected):
        actual = Article.create_inserted_item(url)
        assert actual == expected


class TestArticleAppendErrorMessage:
    @pytest.mark.parametrize(
        "article, message, expected",
        [
            (
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                ),
                "test",
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-20 16:17:22.123456+09:00",
                    error_messages=["test"],
                ),
            ),
            (
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                    error_messages=["first"],
                ),
                "test",
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-20 16:17:22.123456+09:00",
                    error_messages=["first", "test"],
                ),
            ),
        ],
    )
    @freeze_time("2022-01-20 16:17:22.123456+09:00")
    def test_normal(self, article: Article, message: str, expected: Article):
        article.append_error_message(message)
        assert article == expected


class TestArticleGetErrorCount:
    @pytest.mark.parametrize(
        "article, expected",
        [
            (
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                ),
                0,
            ),
            (
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                    error_messages=["test"],
                ),
                1,
            ),
            (
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                    error_messages=["test", "aaa"],
                ),
                2,
            ),
        ],
    )
    def test_normal(self, article: Article, expected: int):
        assert article.get_error_count() == expected


class TestArticleUpdateToInformed:
    @pytest.mark.parametrize(
        "article, parsed_article_data, expected",
        [
            (
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                ),
                ParsedArticleData(
                    title="test", title_ja="テスト", category="Manga", thumbnail="bbbb"
                ),
                Article(
                    url="1223334444",
                    status=StateArticle.Informed,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-20 16:17:22.123456+09:00",
                    title="test",
                    title_ja="テスト",
                    category="Manga",
                    thumbnail="bbbb",
                ),
            ),
            (
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                    error_messages=["test"],
                ),
                ParsedArticleData(
                    title="test", title_ja="テスト", category="Manga", thumbnail="bbbb"
                ),
                Article(
                    url="1223334444",
                    status=StateArticle.Informed,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-20 16:17:22.123456+09:00",
                    error_messages=[],
                    title="test",
                    title_ja="テスト",
                    category="Manga",
                    thumbnail="bbbb",
                ),
            ),
        ],
    )
    @freeze_time("2022-01-20 16:17:22.123456+09:00")
    def test_normal(
        self,
        article: Article,
        parsed_article_data: ParsedArticleData,
        expected: Article,
    ):
        article.update_to_informed(parsed_article_data)
        assert article == expected


class TestArticlePutItem:
    @pytest.mark.parametrize(
        "dynamodb, article, expected",
        [
            (
                {"article": None},
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                ),
                [
                    Article(
                        url="1223334444",
                        status=StateArticle.Inserted,
                        created_at="2022-01-09 16:17:22.123456+09:00",
                        updated_at="2022-01-09 16:17:22.123456+09:00",
                    )
                ],
            ),
            (
                {"article": "上書きテスト1"},
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-20 16:17:22.123456+09:00",
                ),
                [
                    Article(
                        url="1223334444",
                        status=StateArticle.Inserted,
                        created_at="2022-01-09 16:17:22.123456+09:00",
                        updated_at="2022-01-20 16:17:22.123456+09:00",
                    )
                ],
            ),
        ],
        indirect=["dynamodb"],
    )
    def test_normal(
        self,
        dynamodb: DynamoDBServiceResource,
        article: Article,
        expected: List[Article],
    ):
        table = dynamodb.Table("article")
        article.put_item(table)

        assert set([Article(**x) for x in table.scan().get("Items", [])]) == set(
            expected
        )

    @pytest.mark.parametrize(
        "dynamodb, article, expected",
        [
            (
                {"article": None},
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                ),
                [
                    Article(
                        url="1223334444",
                        status=StateArticle.Inserted,
                        created_at="2022-01-09 16:17:22.123456+09:00",
                        updated_at="2022-01-09 16:17:22.123456+09:00",
                    )
                ],
            ),
        ],
        indirect=["dynamodb"],
    )
    def test_normal_with_condition(
        self,
        dynamodb: DynamoDBServiceResource,
        article: Article,
        expected: List[Article],
    ):
        table = dynamodb.Table("article")
        article.put_item(table, Attr("url").not_exists())

        assert set([Article(**x) for x in table.scan().get("Items", [])]) == set(
            expected
        )

    @pytest.mark.parametrize(
        "dynamodb, article, expected",
        [
            (
                {"article": "上書きテスト1"},
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-20 16:17:22.123456+09:00",
                ),
                [
                    Article(
                        url="1223334444",
                        status=StateArticle.Inserted,
                        created_at="2022-01-09 16:17:22.123456+09:00",
                        updated_at="2022-01-20 16:17:22.123456+09:00",
                    )
                ],
            ),
        ],
        indirect=["dynamodb"],
    )
    def test_exception_with_condition(
        self,
        dynamodb: DynamoDBServiceResource,
        article: Article,
        expected: List[Article],
    ):
        table = dynamodb.Table("article")
        try:
            article.put_item(table, Attr("url").not_exists())
        except ClientError as e:
            assert e.response["Error"]["Code"] == "ConditionalCheckFailedException"


class TestArticleGetItem:
    @pytest.mark.parametrize(
        "dynamodb, url, expected",
        [
            (
                {"article": "複数データ1"},
                "1223334444",
                Article(
                    url="1223334444",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                ),
            ),
            (
                {"article": "複数データ1"},
                "abbcccdddd",
                Article(
                    url="abbcccdddd",
                    status=StateArticle.Inserted,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-01-09 16:17:22.123456+09:00",
                ),
            ),
            (
                {"article": "複数データ1"},
                "xyyzzz",
                Article(
                    url="xyyzzz",
                    status=StateArticle.Informed,
                    created_at="2022-01-09 16:17:22.123456+09:00",
                    updated_at="2022-09-19 18:39:34.536831+09:00",
                    title="test",
                    title_ja="テスト",
                    category="Manga",
                    thumbnail="122333",
                ),
            ),
        ],
        indirect=["dynamodb"],
    )
    def test_normal(
        self, dynamodb: DynamoDBServiceResource, url: str, expected: Article
    ):
        table = dynamodb.Table("article")
        actual = Article.get_item(url, table)
        assert actual == expected


class TestArticleQuery:
    @pytest.mark.parametrize(
        "dynamodb, status, expected",
        [
            (
                {"article": "複数データ1"},
                StateArticle.Inserted,
                [
                    Article(
                        url="1223334444",
                        status=StateArticle.Inserted,
                        created_at="2022-01-09 16:17:22.123456+09:00",
                        updated_at="2022-01-09 16:17:22.123456+09:00",
                    ),
                    Article(
                        url="abbcccdddd",
                        status=StateArticle.Inserted,
                        created_at="2022-01-09 16:17:22.123456+09:00",
                        updated_at="2022-01-09 16:17:22.123456+09:00",
                    ),
                ],
            ),
            (
                {"article": "複数データ1"},
                StateArticle.Informed,
                [
                    Article(
                        url="xyyzzz",
                        status=StateArticle.Informed,
                        created_at="2022-01-09 16:17:22.123456+09:00",
                        updated_at="2022-09-19 18:39:34.536831+09:00",
                        title="test",
                        title_ja="テスト",
                        category="Manga",
                        thumbnail="122333",
                    ),
                ],
            ),
        ],
        indirect=["dynamodb"],
    )
    def test_normal(
        self,
        dynamodb: DynamoDBServiceResource,
        status: StateArticle,
        expected: List[Article],
    ):
        table = dynamodb.Table("article")
        actual = Article.query(status, table)
        assert set(actual) == set(expected)

    @pytest.mark.parametrize(
        "dynamodb, status, expected",
        [
            (
                {"article": "複数データ1"},
                StateArticle.Inserted,
                [
                    Article(
                        url="1223334444",
                        status=StateArticle.Inserted,
                        created_at="2022-01-09 16:17:22.123456+09:00",
                        updated_at="2022-01-09 16:17:22.123456+09:00",
                    ),
                    Article(
                        url="abbcccdddd",
                        status=StateArticle.Inserted,
                        created_at="2022-01-09 16:17:22.123456+09:00",
                        updated_at="2022-01-09 16:17:22.123456+09:00",
                    ),
                ],
            ),
        ],
        indirect=["dynamodb"],
    )
    def test_normal_with_limit(
        self,
        dynamodb: DynamoDBServiceResource,
        status: StateArticle,
        expected: List[Article],
    ):
        table = dynamodb.Table("article")
        actual = Article.query(status, table, limit=1)
        assert set(actual) == set(expected)

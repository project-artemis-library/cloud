from dataclasses import dataclass
from typing import List

import feedparser
import pytest
from botocore.exceptions import ClientError
from freezegun import freeze_time
from mypy_boto3_dynamodb import DynamoDBServiceResource
from pytest import MonkeyPatch

import handlers.get_feed as index
from models.article import Article, StateArticle


@dataclass(frozen=True)
class Text:
    text: str


class TestLoadEnvironment:
    @pytest.mark.parametrize(
        "set_environ, expected",
        [
            (
                {"DYNAMODB_TABLE_NAME": "sinofseven"},
                index.EnvironmentVariables(dynamodb_table_name="sinofseven"),
            )
        ],
        indirect=["set_environ"],
    )
    @pytest.mark.usefixtures("set_environ")
    def test_normal(self, expected):
        actual = index.load_environment()
        assert actual == expected


class TestGetFeedEntries:
    @pytest.mark.parametrize(
        "feed, expected",
        [
            (
                {
                    "entries": [
                        {
                            "link": "https://e-hentai.org/g/2330808/37cfac63e0/",
                            "title": "[Doujinshi] (C100) [INS-mode (Amanagi Seiji)] Oyasumi, Onii-chan",
                            "summary": "parody:original, group:ins-mode, artist:amanagi seiji, male:sole male, female:hair buns, female:sister, female:sole female, female:stockings, mixed:incest, other:multi-work series https://www.melonbooks.co.jp/detail/detail.php?product_id=1588328",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330807/7e1d0dea77/",
                            "title": "[Manga] [Jの覚醒とWの本能]エッチな体験談告白投稿男塾より！[中国翻译]",
                            "summary": "language:chinese, language:translated, male:first person perspective, female:filming, female:milf, other:full color, other:mosaic censorship, other:story arc 无授权转载，侵删",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330806/ce58d95bd2/",
                            "title": "[Artist CG] beautiful",
                            "summary": "other:forbidden content",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330758/efd417415c/",
                            "title": "[Manga] [Maemukina Do M] Ingoku Tower Mansion 6 ～Wakaraseya × Akutokubengoshi～",
                            "summary": "artist:itami, male:anal, male:anal intercourse, male:blowjob, male:bondage, male:glasses, male:males only, male:sex toys, male:yaoi, other:multi-work series https://www.dlsite.com/bl-pro/work/=/product_id/BJ580856.html",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330756/df369f809d/",
                            "title": "[Non-H] Last Origin Character Art",
                            "summary": "parody:last origin, female:big ass, female:big breasts, female:bikini, female:huge breasts, female:swimsuit ALL NEW ART IS AT THE END OF THE GALLERYNew art:Hyena Swimsuit DamagedErato WeddingMuse WeddingI have personally created a torrent so the files are in the correct order. Also, could people expunge/delete their old torrents please. The torrent page is too cluttered, there should only ever be 1 torrent there, which is the most current version of the gallery.I will be looking at updating the GIF/MP4 gallery soon.",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330749/1c5313171c/",
                            "title": "[Image Set] Olephia And Zaiha Collection",
                            "summary": "female:yuri",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330745/b3d0811bea/",
                            "title": "[Western] [Barretxiii] Barr's Mares",
                            "summary": "artist:barretxiii, female:big breasts, other:western imageset",
                        },
                    ]
                },
                [
                    index.EntrySummary(
                        link="https://e-hentai.org/g/2330808/37cfac63e0/",
                        title="[Doujinshi] (C100) [INS-mode (Amanagi Seiji)] Oyasumi, Onii-chan",
                        summary="parody:original, group:ins-mode, artist:amanagi seiji, male:sole male, female:hair buns, female:sister, female:sole female, female:stockings, mixed:incest, other:multi-work series https://www.melonbooks.co.jp/detail/detail.php?product_id=1588328",
                    ),
                    index.EntrySummary(
                        link="https://e-hentai.org/g/2330807/7e1d0dea77/",
                        title="[Manga] [Jの覚醒とWの本能]エッチな体験談告白投稿男塾より！[中国翻译]",
                        summary="language:chinese, language:translated, male:first person perspective, female:filming, female:milf, other:full color, other:mosaic censorship, other:story arc 无授权转载，侵删",
                    ),
                    index.EntrySummary(
                        link="https://e-hentai.org/g/2330806/ce58d95bd2/",
                        title="[Artist CG] beautiful",
                        summary="other:forbidden content",
                    ),
                    index.EntrySummary(
                        link="https://e-hentai.org/g/2330758/efd417415c/",
                        title="[Manga] [Maemukina Do M] Ingoku Tower Mansion 6 ～Wakaraseya × Akutokubengoshi～",
                        summary="artist:itami, male:anal, male:anal intercourse, male:blowjob, male:bondage, male:glasses, male:males only, male:sex toys, male:yaoi, other:multi-work series https://www.dlsite.com/bl-pro/work/=/product_id/BJ580856.html",
                    ),
                    index.EntrySummary(
                        link="https://e-hentai.org/g/2330756/df369f809d/",
                        title="[Non-H] Last Origin Character Art",
                        summary="parody:last origin, female:big ass, female:big breasts, female:bikini, female:huge breasts, female:swimsuit ALL NEW ART IS AT THE END OF THE GALLERYNew art:Hyena Swimsuit DamagedErato WeddingMuse WeddingI have personally created a torrent so the files are in the correct order. Also, could people expunge/delete their old torrents please. The torrent page is too cluttered, there should only ever be 1 torrent there, which is the most current version of the gallery.I will be looking at updating the GIF/MP4 gallery soon.",
                    ),
                    index.EntrySummary(
                        link="https://e-hentai.org/g/2330749/1c5313171c/",
                        title="[Image Set] Olephia And Zaiha Collection",
                        summary="female:yuri",
                    ),
                    index.EntrySummary(
                        link="https://e-hentai.org/g/2330745/b3d0811bea/",
                        title="[Western] [Barretxiii] Barr's Mares",
                        summary="artist:barretxiii, female:big breasts, other:western imageset",
                    ),
                ],
            )
        ],
    )
    def test_normal(
        self, monkeypatch: MonkeyPatch, feed: dict, expected: List[index.EntrySummary]
    ):
        monkeypatch.setattr(feedparser, "parse", lambda _: feed)
        actual = index.get_feed_entries()
        assert set(actual) == set(expected)


class TestIsTargetCategory:
    @pytest.mark.parametrize(
        "title, expected",
        [
            (
                Text(
                    "[Doujinshi] (C100) [INS-mode (Amanagi Seiji)] Oyasumi, Onii-chan"
                ),
                True,
            ),
            (Text("[Manga] [Jの覚醒とWの本能]エッチな体験談告白投稿男塾より！[中国翻译]"), True),
            (Text("[Artist CG] beautiful"), True),
            (
                Text(
                    "[Manga] [Maemukina Do M] Ingoku Tower Mansion 6 ～Wakaraseya × Akutokubengoshi～"
                ),
                True,
            ),
            (Text("[Non-H] Last Origin Character Art"), False),
            (Text("[Image Set] Olephia And Zaiha Collection"), False),
            (Text("[Western] [Barretxiii] Barr's Mares"), False),
        ],
    )
    def test_normal(self, title: Text, expected: bool):
        actual = index.is_target_category(title.text)
        assert actual == expected


class TestHasForeignerLanguageTag:
    @pytest.mark.parametrize(
        "summary, expected",
        [
            (
                Text(
                    "parody:original, group:ins-mode, artist:amanagi seiji, male:sole male, female:hair buns, female:sister, female:sole female, female:stockings, mixed:incest, other:multi-work series https://www.melonbooks.co.jp/detail/detail.php?product_id=1588328"
                ),
                False,
            ),
            (
                Text(
                    "language:chinese, language:translated, male:first person perspective, female:filming, female:milf, other:full color, other:mosaic censorship, other:story arc 无授权转载，侵删"
                ),
                True,
            ),
            (Text("other:forbidden content"), False),
            (
                Text(
                    "artist:itami, male:anal, male:anal intercourse, male:blowjob, male:bondage, male:glasses, male:males only, male:sex toys, male:yaoi, other:multi-work series https://www.dlsite.com/bl-pro/work/=/product_id/BJ580856.html"
                ),
                False,
            ),
            (
                Text(
                    "parody:last origin, female:big ass, female:big breasts, female:bikini, female:huge breasts, female:swimsuit ALL NEW ART IS AT THE END OF THE GALLERYNew art:Hyena Swimsuit DamagedErato WeddingMuse WeddingI have personally created a torrent so the files are in the correct order. Also, could people expunge/delete their old torrents please. The torrent page is too cluttered, there should only ever be 1 torrent there, which is the most current version of the gallery.I will be looking at updating the GIF/MP4 gallery soon."
                ),
                False,
            ),
            (Text("female:yuri"), False),
            (
                Text("artist:barretxiii, female:big breasts, other:western imageset"),
                False,
            ),
        ],
    )
    def test_normal(self, summary: Text, expected: bool):
        actual = index.has_foreigner_language_tag(summary.text)
        assert actual == expected


class TestInsertArticle:
    @pytest.mark.parametrize(
        "dynamodb, url, expected",
        [
            (
                {"article": None},
                "1223334444",
                [
                    Article(
                        url="1223334444",
                        status=StateArticle.Inserted,
                        created_at="2022-02-22 11:11:11.123456+09:00",
                        updated_at="2022-02-22 11:11:11.123456+09:00",
                    )
                ],
            ),
            (
                {"article": "上書きテスト1"},
                "1223334444",
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
    @freeze_time("2022-02-22 11:11:11.123456+09:00")
    def test_normal(
        self, dynamodb: DynamoDBServiceResource, url: str, expected: List[Article]
    ):
        table = dynamodb.Table("article")

        index.insert_article(url, table)

        resp = table.scan()

        assert set([Article(**x) for x in resp.get("Items", [])]) == set(expected)

    @pytest.mark.parametrize(
        "dynamodb, url",
        [
            (
                {"article": None},
                "1223334444",
            ),
        ],
        indirect=["dynamodb"],
    )
    def test_normal(
        self, monkeypatch: MonkeyPatch, dynamodb: DynamoDBServiceResource, url: str
    ):
        def dummy(*args, **kwargs):
            raise ClientError(
                {
                    "Status": "Error",
                    "StatusReason": "Error",
                    "Error": {"Code": "200", "Message": "Test"},
                    "ResponseMetadata": {
                        "RequestId": "id",
                        "HostId": "id",
                        "HTTPStatusCode": 200,
                        "HTTPHeaders": {},
                        "RetryAttempts": 2,
                    },
                },
                "test",
            )

        table = dynamodb.Table("article")
        monkeypatch.setattr(table, "put_item", dummy)

        with pytest.raises(ClientError):
            index.insert_article(url, table)


class TestMain:
    @pytest.mark.parametrize(
        "set_environ, dynamodb, feed_entries, expected",
        [
            (
                {"DYNAMODB_TABLE_NAME": "article"},
                {"article": None},
                {
                    "entries": [
                        {
                            "link": "https://e-hentai.org/g/2330808/37cfac63e0/",
                            "title": "[Doujinshi] (C100) [INS-mode (Amanagi Seiji)] Oyasumi, Onii-chan",
                            "summary": "parody:original, group:ins-mode, artist:amanagi seiji, male:sole male, female:hair buns, female:sister, female:sole female, female:stockings, mixed:incest, other:multi-work series https://www.melonbooks.co.jp/detail/detail.php?product_id=1588328",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330807/7e1d0dea77/",
                            "title": "[Manga] [Jの覚醒とWの本能]エッチな体験談告白投稿男塾より！[中国翻译]",
                            "summary": "language:chinese, language:translated, male:first person perspective, female:filming, female:milf, other:full color, other:mosaic censorship, other:story arc 无授权转载，侵删",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330806/ce58d95bd2/",
                            "title": "[Artist CG] beautiful",
                            "summary": "other:forbidden content",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330758/efd417415c/",
                            "title": "[Manga] [Maemukina Do M] Ingoku Tower Mansion 6 ～Wakaraseya × Akutokubengoshi～",
                            "summary": "artist:itami, male:anal, male:anal intercourse, male:blowjob, male:bondage, male:glasses, male:males only, male:sex toys, male:yaoi, other:multi-work series https://www.dlsite.com/bl-pro/work/=/product_id/BJ580856.html",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330756/df369f809d/",
                            "title": "[Non-H] Last Origin Character Art",
                            "summary": "parody:last origin, female:big ass, female:big breasts, female:bikini, female:huge breasts, female:swimsuit ALL NEW ART IS AT THE END OF THE GALLERYNew art:Hyena Swimsuit DamagedErato WeddingMuse WeddingI have personally created a torrent so the files are in the correct order. Also, could people expunge/delete their old torrents please. The torrent page is too cluttered, there should only ever be 1 torrent there, which is the most current version of the gallery.I will be looking at updating the GIF/MP4 gallery soon.",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330749/1c5313171c/",
                            "title": "[Image Set] Olephia And Zaiha Collection",
                            "summary": "female:yuri",
                        },
                        {
                            "link": "https://e-hentai.org/g/2330745/b3d0811bea/",
                            "title": "[Western] [Barretxiii] Barr's Mares",
                            "summary": "artist:barretxiii, female:big breasts, other:western imageset",
                        },
                    ]
                },
                [
                    Article(
                        url="https://e-hentai.org/g/2330808/37cfac63e0/",
                        status=StateArticle.Inserted,
                        created_at="2022-02-01 11:11:11.123456+09:00",
                        updated_at="2022-02-01 11:11:11.123456+09:00",
                    ),
                    Article(
                        url="https://e-hentai.org/g/2330806/ce58d95bd2/",
                        status=StateArticle.Inserted,
                        created_at="2022-02-01 11:11:11.123456+09:00",
                        updated_at="2022-02-01 11:11:11.123456+09:00",
                    ),
                    Article(
                        url="https://e-hentai.org/g/2330758/efd417415c/",
                        status=StateArticle.Inserted,
                        created_at="2022-02-01 11:11:11.123456+09:00",
                        updated_at="2022-02-01 11:11:11.123456+09:00",
                    ),
                ],
            )
        ],
        indirect=["set_environ", "dynamodb"],
    )
    @pytest.mark.usefixtures("set_environ")
    @freeze_time("2022-02-01 11:11:11.123456+09:00")
    def test_normal(self, monkeypatch, dynamodb, feed_entries, expected):
        monkeypatch.setattr(feedparser, "parse", lambda _: feed_entries)
        index.main(dynamodb_resource=dynamodb)

        table = dynamodb.Table("article")
        resp = table.scan()
        assert set([Article(**x) for x in resp.get("Items", [])]) == set(expected)

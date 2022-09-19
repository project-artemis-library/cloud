import pytest
from freezegun import freeze_time
from utils.datetime import now


class TestNow(object):
    @pytest.mark.parametrize(
        'base, expected', [
            (
                "2022-09-19 15:34:13.711072+09:00",
                "2022-09-19 15:34:13.711072+09:00"
            ),
            (
                "2022-09-19 15:34:13.711072+00:00",
                "2022-09-20 00:34:13.711072+09:00"
            ),
        ]
    )
    def test_normal(self, base, expected):
        with freeze_time(base):
            actual = now()
            assert str(actual) == str(expected)

"""Tests for recall pagination."""

import pytest

from organizational_memory.recall.pagination import paginate


def test_first_page_has_more() -> None:
    page = paginate(list(range(10)), limit=3, offset=0)
    assert page.items == [0, 1, 2]
    assert page.total == 10
    assert page.returned == 3
    assert page.has_more is True


def test_last_page_no_more() -> None:
    page = paginate(list(range(10)), limit=3, offset=9)
    assert page.items == [9]
    assert page.has_more is False


def test_no_limit_returns_rest() -> None:
    page = paginate(list(range(5)), offset=2)
    assert page.items == [2, 3, 4]
    assert page.has_more is False


def test_negative_offset_treated_as_zero() -> None:
    page = paginate(list(range(3)), offset=-5)
    assert page.items == [0, 1, 2]
    assert page.offset == 0


def test_negative_limit_raises() -> None:
    with pytest.raises(ValueError, match="limit"):
        paginate([1, 2, 3], limit=-1)


def test_metadata() -> None:
    page = paginate(list(range(10)), limit=4, offset=4)
    assert page.as_metadata() == {
        "total": 10,
        "offset": 4,
        "limit": 4,
        "returned": 4,
        "has_more": True,
    }


def test_offset_beyond_end_is_empty() -> None:
    page = paginate([1, 2], limit=5, offset=10)
    assert page.items == []
    assert page.has_more is False

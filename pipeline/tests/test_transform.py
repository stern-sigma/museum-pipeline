#pylint: skip-file
from unittest.mock import MagicMock

import pytest
import datetime

from museum_pipeline.transform import (_prepare_upload_data, _prepare_upload_data_row, filter_strings)


ID_DICT = {
    'exhibition': {1: 1, 0: 2, 5: 3, 2: 4, 4: 5, 3: 6},
    'rating': {0: 1, 1: 2, 2: 3, 3: 4, 4: 5},
    'request': {0: 1, 1: 2}
}


@pytest.mark.parametrize("row,result", [
    [
        {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": ""},
        {"table": "rating",
         "data":
         {"event_at": datetime.datetime(
             year=2023, month=3, day=6, hour=15, minute=9, second=21),
          "exhibition_id": 5, "value_id": 1}}
    ],
    [
        {"at": "2023-03-06 15:09:21", "site": "3", "val": "-1", "type": "1.0"},
        {"table": "request",
         "data":
         {"event_at": datetime.datetime(
            year=2023, month=3, day=6, hour=15, minute=9, second=21),
          "exhibition_id": 6, "value_id": 2}}
    ],
    [
        {"at": "2023-03-06 15:09:21", "site": "3", "val": "-1", "type": "0.0"},
        {"table": "request",
         "data":
         {"event_at": datetime.datetime(
            year=2023, month=3, day=6, hour=15, minute=9, second=21),
          "exhibition_id": 6, "value_id": 1}}
    ]
]
)
def test__prepare_upload_data_row(row, result):
    assert _prepare_upload_data_row(row, ID_DICT) == result


@pytest.mark.parametrize("row", [
    {"at": None, "site": "4", "val": "0", "type": ""},
    {"at": 123, "site": "4", "val": "0", "type": ""},
    {"at": 123.45, "site": "4", "val": "0", "type": ""},
    {"at": True, "site": "4", "val": "0", "type": ""},
    {"at": ["list", "of", "values"], "site": "4", "val": "0", "type": ""},
    {"at": {"nested": "dict"}, "site": "4", "val": "0", "type": ""},
    {"at": {1, 2, 3}, "site": "4", "val": "0", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": None, "val": "0", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": 567, "val": "0", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": 56.78, "val": "0", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": False, "val": "0", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": ["example", "list"], "val": "0", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": {"other": "nested"}, "val": "0", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": {4, 5, 6}, "val": "0", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": None, "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": 789, "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": 89.01, "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": True, "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": ["another", "list"], "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": {"key": "value"}, "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": {7, 8, 9}, "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": None},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": 123},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": 45.67},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": False},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": ["final", "list"]},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": {"another": "dict"}},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": {10, 11, 12}}
])
def test_typeerror_upload_data_row(row):
    with pytest.raises(TypeError):
        _prepare_upload_data_row(row)


@pytest.mark.parametrize("row", [
    {"at": "foo", "site": "4", "val": "0", "type": ""},
    {"at": "20203-03-06 15:09:21", "site": "foo", "val": "0", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": "f", "type": ""},
    {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": "foo"}
])
def test_valueerror_upload_data_row(row):
    with pytest.raises(ValueError):
        _prepare_upload_data_row(row, ID_DICT)


@pytest.mark.parametrize("row", [
        {"site": "4", "val": "0", "type": ""},
        {"at": "2023-03-06 15:09:21", "val": "0", "type": ""},
        {"at": "2023-03-06 15:09:21", "site": "4", "type": ""},
        {"at": "2023-03-06 15:09:21", "site": "4", "val": "0"}
])
def test_keyerror_upload_data_row(row):
    with pytest.raises(KeyError):
        _prepare_upload_data_row(row, ID_DICT)


def test_prepare_upload_data_good():
    inp = [
        {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": ""},
        {"at": "2023-03-06 15:09:21", "site": "3", "val": "-1", "type": "1.0"},
        {"at": "2023-03-06 15:09:21", "site": "3", "val": "-1", "type": "0.0"},
    ]
    out = {
        "rating": [
            {"event_at": datetime.datetime(
             year=2023, month=3, day=6, hour=15, minute=9, second=21),
                "exhibition_id": 5, "value_id": 1}
        ],
        "request": [
            {"event_at": datetime.datetime(
                year=2023, month=3, day=6, hour=15, minute=9, second=21),
                "exhibition_id": 6, "value_id": 2},
            {"event_at": datetime.datetime(
                year=2023, month=3, day=6, hour=15, minute=9, second=21),
                "exhibition_id": 6, "value_id": 1}
            ]
    }
    logger = MagicMock()
    assert _prepare_upload_data(inp, ID_DICT, logger) == out


def test_prepare_upload_data_bad():
    inp = [
        {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": ""},
        {"at": "2023-03-06 15:09:21", "site": "3", "val": "-1", "type": "1.0"},
        {"at": "2023-03-06 15:09:21", "site": "3", "val": "-1", "type": "f.0"},
    ]
    out = {
        "rating": [
            {"event_at": datetime.datetime(
             year=2023, month=3, day=6, hour=15, minute=9, second=21),
                "exhibition_id": 5, "value_id": 1}
        ],
        "request": [
            {"event_at": datetime.datetime(
                year=2023, month=3, day=6, hour=15, minute=9, second=21),
                "exhibition_id": 6, "value_id": 2}
            ]
    }
    logger = MagicMock()
    assert _prepare_upload_data(inp, ID_DICT, logger) == out


def test_prepare_upload_data_bad_log():
    inp = [
        {"at": "2023-03-06 15:09:21", "site": "4", "val": "0", "type": ""},
        {"at": "2023-03-06 15:09:21", "site": "3", "val": "-1", "type": "1.0"},
        {"at": "2023-03-06 15:09:21", "site": "3", "val": "-1", "type": "f.0"},
    ]
    out = {
        "rating": [
            {"event_at": datetime.datetime(
             year=2023, month=3, day=6, hour=15, minute=9, second=21),
                "exhibition_id": 5, "value_id": 1}
        ],
        "request": [
            {"event_at": datetime.datetime(
                year=2023, month=3, day=6, hour=15, minute=9, second=21),
                "exhibition_id": 6, "value_id": 2}
            ]
    }
    logger = MagicMock()
    _prepare_upload_data(inp, ID_DICT, logger) == out
    assert logger.exception.called


@pytest.mark.parametrize("inp,pattern,out",
                         [
                            [["αβγ", "δεζ", "ηθι"], r"αβγ", ["αβγ"]],
                            [["ápple", "banana", "âvocado"], r"á.*", ["ápple"]],
                            [["１２３", "abc", "３４５", "い89"], r"[１２３４５６７８９]+", ["１２３", "３４５"]],
                            [["🍎", "🐶", "🍏🍎", "scatter"], r".*🍎.*", ["🍎", "🍏🍎"]],
                            [["🍓", "🍌", "🍐"], r"🍇", []],
                            [[], r".*", []],
                            [["★", "♠", "♥", "abc"], r"^[★♠]*$", ["★", "♠"]],
                            [["一二", "三四五", "七八"], r"^.{2}$", ["一二", "七八"]],
                            [["абв123", "!!", "язы789", "😊+abc"], r"^[а-яА-Я0-9]+$", ["абв123", "язы789"]],
                            [["file🌟.txt", "file🌟.csv", "file💡.json"], r"file🌟\.txt", ["file🌟.txt"]],
                            ])
def test_filter_strings(inp, pattern, out):
    assert filter_strings(inp, pattern) == out

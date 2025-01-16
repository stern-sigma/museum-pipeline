#pylint: skip-file
from unittest.mock import MagicMock
import datetime

import pytest

from museum_pipeline.kafka_pipeline import (process_val, process_site,
                                            process_at, upload_message)


def test_process_val_good():
    message = {"val": 2}
    id_dict = {"rating": {2: 4}}
    out = {"table": "rating", "value_id": 4}
    assert process_val(message, id_dict) == out


def test_process_val_val_missing():
    with pytest.raises(KeyError) as e:
        process_val({}, {2: 4})
    assert "INVALID: Required key, 'val', missing." == e.value.args[0]


def test_process_val_val_not_int():
    with pytest.raises(TypeError) as e:
        process_val({"val": "foo"}, {})
    assert e.value.args[0] == "INVALID: Illegal type for field 'val'."


def test_process_val_type_good():
    message = {"val": -1, "type": 1}
    id_dict = {"request": {1: 2}}
    out = {"table": "request", "value_id": 2}
    assert process_val(message, id_dict) == out


def test_process_val_type_missing():
    message = {"val": -1}
    id_dict = {"request": {1: 2}}
    with pytest.raises(KeyError) as e:
        process_val(message, id_dict)
    assert e.value.args[0] == "INVALID: 'type' key missing for val of -1."


def test_process_val_type_not_int():
    with pytest.raises(TypeError) as e:
        process_val({"val": -1, "type": "foo"}, {})
    assert e.value.args[0] == "INVALID: Illegal type for field 'type'."


def test_process_val_type_unrecognised():
    with pytest.raises(ValueError) as e:
        process_val({"val": -1, "type": 2}, {"request": {}})
    assert e.value.args[0] == "INVALID: Unrecognised value for field 'type'."


def test_process_val_val_unrecognised():
    with pytest.raises(ValueError) as e:
        process_val({"val": 2}, {"rating": {}})
    assert e.value.args[0] == "INVALID: Unrecognised value for field 'val'."


def test_process_site_good():
    assert process_site({"site": "2"}, {2: 4}) == {"exhibition_id": 4}


def test_process_site_missing():
    with pytest.raises(KeyError) as e:
        process_site({}, {})
    assert e.value.args[0] == "INVALID: Required key, 'site', missing."


def test_process_site_not_int():
    with pytest.raises(ValueError) as e:
        process_site({"site": "foo"}, {})
    assert e.value.args[0] == "INVALID: Illegal value for field 'site'."


def test_process_site_unrecognised():
    with pytest.raises(ValueError) as e:
        process_site({"site": "2"}, {})
    assert e.value.args[0] == "INVALID: Unrecognised value for field 'site'."


def test_process_at_good():
    as_str = "2025-01-13T09:23:20.177598+00:00"
    as_obj = datetime.datetime(2025, 1, 13, 9, 23, 20, 177598,
                               tzinfo=datetime.timezone.utc)
    start = datetime.time(hour=8, minute=45)
    end = datetime.time(hour=18, minute=15)
    assert process_at({"at": as_str}, start, end) == {"event_at": as_obj}


def test_process_at_bad():
    with pytest.raises(ValueError):
        start = datetime.time(hour=8, minute=45)
        end = datetime.time(hour=18, minute=15)
        process_at({"at": "foo"}, start, end)


def test_process_at_early():
    as_str = "2025-01-13T03:23:20.177598+00:00"
    start = datetime.time(hour=8, minute=45)
    end = datetime.time(hour=18, minute=15)
    with pytest.raises(ValueError) as e:
        process_at({"at": as_str}, start, end)
    assert e.value.args[0] == "INVALID: You should be asleep."


def test_process_at_late():
    as_str = "2025-01-13T23:23:20.177598+00:00"
    start = datetime.time(hour=8, minute=45)
    end = datetime.time(hour=18, minute=15)
    with pytest.raises(ValueError) as e:
        process_at({"at": as_str}, start, end)
    assert e.value.args[0] == "INVALID: You should be asleep."


def test_upload_message_bad_table():
    with pytest.raises(ValueError) as e:
        upload_message({}, MagicMock())
    assert e.value.args[0] == "INVALID: Table name not recognised."


def test_upload_message_request():
    mock_con = MagicMock()
    mock_cur = MagicMock()
    mock_con.cur.return_value = mock_cur
    upload_message({"table": "request"}, mock_con)
    assert mock_cur.execute.calledwith("""
            INSERT INTO request_interaction
                (event_at, request_id, exhibition_id)
            VALUES
                (%(event_at)s, %(value_id)s, %(exhibition_id)s)
            ;
            """, {"table": "request"})


def test_upload_message_rating():
    mock_con = MagicMock()
    mock_cur = MagicMock()
    mock_con.cur.return_value = mock_cur
    upload_message({"table": "rating"}, mock_con)
    assert mock_cur.execute.calledwith("""
            INSERT INTO rating_interaction
                (event_at, rating_id, exhibition_id)
            VALUES
                (%(event_at)s, %(value_id)s, %(exhibition_id)s)
            ;
            """, {"table": "rating"})

#pylint: skip-file
from unittest.mock import patch, MagicMock, call

import pytest
import botocore

from museum_pipeline.extract import (download_files,
                                     get_filenames,
                                     merge_csvs,
                                     load_csv_data,
                                     load_id_dict
                                     )

@pytest.mark.parametrize("bad_type", [
    3,
    True,
    None,
    2.1,
    [],
    {},
    dict(),
    'a'
])
@patch('boto3.client')
def test_download_files_illegal_client(mock_client, bad_type):
    """Test that download_files raises a TypeError with bad client type."""
    with pytest.raises(TypeError):
        download_files(bad_type, 'a', ['a'])


@pytest.mark.parametrize("bad_type", [
    3,
    True,
    None,
    2.1,
    [],
    {},
    dict()
])
def test_download_files_illegal_bucket_name(bad_type):
    """Test that download_files raises a TypeError with bad bucket names."""
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    with pytest.raises(TypeError):
        download_files(mock_client, bad_type, ['a'])


@pytest.mark.parametrize("bad_files", [
    None,                  # NoneType
    True,                  # bool
    42,                    # int
    3.14,                  # float
    2 + 3j,                # complex
    "hello",               # str
    b"bytes",              # bytes
    [1, 2, 3],             # list
    (1, 2, 3),             # tuple
    {1, 2, 3},             # set
    {"key": "value"},      # dict
    ["hello", 42],            # str and int
    ["hello", {"key": "value"}],  # str and dict
    ["hello", 3.14],          # str and float
    ["hello", [1, 2, 3]],     # str and list
    ["hello", (1, 2, 3)],     # str and tuple
    ["hello", {1, 2, 3}]  # str and set
])
def test_download_files_illegal_files(bad_files):
    """Test that download_files raises a TypeError with bad filename type."""
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    with pytest.raises(TypeError):
        download_files(mock_client, 'a', bad_files)


@pytest.mark.parametrize("good_bucket, good_file,expected_call", [
    ["abcdefg", ["hijklmn", "opqr", "stuv"], [("abcdefg", "hijklmn", "data/hijklmn"), ("abcdefg", "opqr", "data/opqr"), ("abcdefg", "stuv", "data/stuv")]],
    ["wxyz", ["abcd", "efgh", "ijklmnopqr"], [("wxyz", "abcd", "data/abcd"), ("wxyz", "efgh", "data/efgh"), ("wxyz", "ijklmnopqr", "data/ijklmnopqr")]],
    ["mnopqrst", ["uvwx", "yzabcdefg", "hijkl"], [("mnopqrst", "uvwx", "data/uvwx"), ("mnopqrst", "yzabcdefg", "data/yzabcdefg"), ("mnopqrst", "hijkl", "data/hijkl")]],
    ["uvwxyz", ["abcdef", "gh", "ijklmnop"], [("uvwxyz", "abcdef", "data/abcdef"), ("uvwxyz", "gh", "data/gh"), ("uvwxyz", "ijklmnop", "data/ijklmnop")]],
    ["a", ["b", "cdefghij", "klmnopq"], [("a", "b", "data/b"), ("a", "cdefghij", "data/cdefghij"), ("a", "klmnopq", "data/klmnopq")]],
    ["Ωπ@", ["ç", "åäöüßé", "êçøñ"], [("Ωπ@", "ç", "data/ç"), ("Ωπ@", "åäöüßé", "data/åäöüßé"), ("Ωπ@", "êçøñ", "data/êçøñ")]],
    ["∆π₹", ["∞", "Ωπ∞", "$&π"], [("∆π₹", "∞", "data/∞"), ("∆π₹", "Ωπ∞", "data/Ωπ∞"), ("∆π₹", "$&π", "data/$&π")]],
    ["Ὠπ", ["123", "≠Ωπ", "ßåä"], [("Ὠπ", "123", "data/123"), ("Ὠπ", "≠Ωπ", "data/≠Ωπ"), ("Ὠπ", "ßåä", "data/ßåä")]],
    ["£π@€Ω", ["π", "&πΩπ@", "✓øπë"], [("£π@€Ω", "π", "data/π"), ("£π@€Ω", "&πΩπ@", "data/&πΩπ@"), ("£π@€Ω", "✓øπë", "data/✓øπë")]],
    ["π∞Ωπ", ["Ωπ@__", "∞ππ", "Ωππππ"], [("π∞Ωπ", "Ωπ@__", "data/Ωπ@__"), ("π∞Ωπ", "∞ππ", "data/∞ππ"), ("π∞Ωπ", "Ωππππ", "data/Ωππππ")]]
])
def test_download_files_good(good_bucket, good_file, expected_call):
    """Test that download_files calls download_objects correctly."""
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_download = MagicMock()
    mock_client.download_file = mock_download
    download_files(mock_client, good_bucket, good_file)
    print(mock_download.call_args_list)
    for c in expected_call:
        assert call(*c) in mock_download.call_args_list


@pytest.mark.parametrize("outputs,expected_out",
    [
        [
            {
                "Contents": [
                    {"Key": "jqBp8V&^kZ"},
                    {"Key": "tL@m#12$Wz"},
                    {"Key": "o7Y@!%xVp"}
                ]
            },
            [
                "jqBp8V&^kZ",
                "tL@m#12$Wz",
                "o7Y@!%xVp"
            ]
        ],
        [
            {
                "Contents": [
                    {"Key": "Uw7&pQ@hZr"},
                    {"Key": "*V9K3$bYx&"},
                    {"Key": "%Rq!P7t^Mw"}
                ]
            },
            [
                "Uw7&pQ@hZr",
                "*V9K3$bYx&",
                "%Rq!P7t^Mw"
            ]
        ],
        [
            {
                "Contents": [
                    {"Key": "F8x^pZtR9&"},
                    {"Key": "!L%W2Mq&9Y"},
                    {"Key": "@XqT7b&Vp^"}
                ]
            },
            [
                "F8x^pZtR9&",
                "!L%W2Mq&9Y",
                "@XqT7b&Vp^"
            ]
        ],
        [
            {
                "Contents": [
                    {"Key": "jV9&xW2K*pq"},
                    {"Key": "oM@Rb7Wt!Y^"},
                    {"Key": "KL@Z9!B8xqR"}
                ]
            },
            [
                "jV9&xW2K*pq",
                "oM@Rb7Wt!Y^",
                "KL@Z9!B8xqR"
            ]
        ],
        [
            {
                "Contents": [
                    {"Key": "*xM7L2Wt&@q"},
                    {"Key": "o8&RbXZ#9tV!"},
                    {"Key": "F@!J7pR2MqKL"}
                ]
            },
            [
                "*xM7L2Wt&@q",
                "o8&RbXZ#9tV!",
                "F@!J7pR2MqKL"
            ]
        ]])
def test_get_filenames(outputs, expected_out):
    """Test that get_filenames behaves as expected."""
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_list_objects_v2 = MagicMock()
    mock_list_objects_v2.return_value = outputs
    mock_client.list_objects_v2 = mock_list_objects_v2
    assert get_filenames(mock_client, 'Foo') == expected_out


@pytest.mark.parametrize("bad_type", [
    3,
    True,
    None,
    2.1,
    [],
    {},
    dict()
])
def test_get_filenames_illegal_bucket_name(bad_type):
    """Test that download_files raises a TypeError with bad bucket names."""
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    with pytest.raises(TypeError):
        get_filenames(mock_client, bad_type)


@pytest.mark.parametrize("bad_type", [
    3,
    True,
    None,
    2.1,
    [],
    {},
    dict(),
    'a'
])
@patch('boto3.client')
def test_get_filenames_illegal_client(mock_client, bad_type):
    """Test that download_files raises a TypeError with bad client type."""
    with pytest.raises(TypeError):
        get_filenames(bad_type, 'a')

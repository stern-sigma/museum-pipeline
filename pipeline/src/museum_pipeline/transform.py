#pylint: disable=unused-variable
import datetime as dt
from re import fullmatch


def _prepare_upload_data(
        data: list[dict],
        id_dict: dict,
        logger,
        limit: int | None = float("inf")) -> dict[str: list[tuple]]: #pylint: disable=unsupported-binary-operation
    """Converts csv-formatted data into a form to be uploaded.

        Arguments:
            data -- a list of dicts, expected to formatted thus:
                [
                    {
                        "at": <str: timestamp "%Y-%m-%d %H:%M:%S>,
                        "site": <str: int component of public_id>,
                        "type": <str: empty | float request_value>,
                        "val": <str: rating_value | -1 if request>
                    },
                    ...
                ]

            id_dict -- id mapping dict, of the form:
                {
                    "exhibition":
                        {
                            "<public_id int component>":<int: row id>,
                            ...
                        },
                    "rating":
                        {
                            "<rating_value>":<int: row id>,
                            ...
                        },
                    "request":
                        {
                            "<request_value>":<int: row id>,
                            ...
                        }
                }

            logger -- logging object

            limit -- int limit of rows to output

        Returns:
            a dictionary containing two lists of dictionaries to upload,
            of the form:
                {
                    "rating":
                        [
                            {
                                "event_at": <datetime>,
                                "exhibition_id": <int: row id of exhibition>,
                                "value_id": <int: row value of rating>
                            },
                            ...
                        ],
                    "request":
                        [
                            {
                                "event_at": <datetime>,
                                "exhibition_id": <int: row id of exhibition>,
                                "value_id": <int: row value of request>
                            },
                            ...
                        ]
                }
    """
    if not isinstance(data, list):
        raise TypeError("Required positional argument 'data' must be a list,"
                        f"not {type(data)}")
    if not isinstance(id_dict, dict):
        raise TypeError("Required positional argument 'id_dict' must be a dict"
                        f", not {type(id_dict)}")
    upload_data = {"rating": [], "request": []}
    if limit is None:
        limit = float("inf")
    row_count = 0
    for row in data:
        if row_count >= limit:
            break
        try:
            processed_row = _prepare_upload_data_row(row, id_dict)
            upload_data[processed_row["table"]].append(processed_row["data"])
            row_count += 1
        except (TypeError, KeyError, ValueError):
            logger.exception(f"Row '{row}' skipped.")
            continue
    return upload_data


def _prepare_upload_data_row(row: dict, id_dict: dict) -> tuple:
    """Converts csv row of expected format to custom dict for uploading.

    Arguments:
        row -- a dictionary with the following strucutre:
            {
                'at': time string, formatted "%Y-%m-%d %H:%M:%S",
                'site': a numeric string, representing the location,
                'val': a numeric string, represting some feature of the event
                    (-1 is also a valid null value),
                'type': a string, which may be empty, or contain float values
            }

    Returns:
        {
            "table": <str: rating | request>
            "data":
                {
                    "event_at": <datetime>,
                    "exhibition_id": <int: row id of exhibition>,
                    "value_id": <int: row value of <rating | request>>
                }
        }
    """
    if not isinstance(row, dict):
        raise TypeError("All elements of 'data' must be dicts."
                        f"Recieved {type(row)} instead.")
    if "at" not in row:
        raise KeyError("Expected column 'at' missing from row.")
    at = dt.datetime.strptime(row["at"], "%Y-%m-%d %H:%M:%S")

    if "site" not in row:
        raise KeyError("Expected column 'site' missing from row.")
    site = row["site"]
    if not isinstance(site, str):
        raise TypeError("Type of column 'site' must be string,"
                        f"not {type(site)}")
    if not site.isnumeric():
        raise ValueError("Value of column 'site' must be numeric.")
    site = int(site)
    if site not in id_dict["exhibition"]:
        raise KeyError(f"Exhibition {row["site"]} not recognised.")
    site = id_dict["exhibition"][site]

    table: str
    if row["type"] == "":
        table = "rating"
    elif fullmatch(r"\d+\.\d+", row["type"]) is not None:
        table = "request"
        row["val"] = str(int(float(row["type"])))
    else:
        raise ValueError(f"Illegal value for type: {row["type"]}")

    if "val" not in row:
        raise KeyError("Expected column 'val' missing from row.")
    val = row["val"]
    if not isinstance(val, str):
        raise TypeError("Type of column 'val' must be a string,"
                        f"not {type(val)}")
    if not val.isnumeric() and val != '-1':
        raise ValueError("Value of column 'val' must be numeric."
                         f"Value: {val}")
    val = int(val)
    if val not in id_dict[table]:
        raise ValueError("Value of column 'val' not recognised; "
                         f"{val} is not a recognised value for {table}.")
    val = id_dict[table][val]
    return {"table": table,
            "data": {"event_at": at, "exhibition_id": site, "value_id": val}}


def filter_strings(to_filter: list[str], pattern: str) -> list[str]:
    """Returns a list of strings matching a pattern.
    """
    return [x for x in to_filter if fullmatch(pattern, x) is not None]

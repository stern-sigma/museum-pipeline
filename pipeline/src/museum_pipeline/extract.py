#pylint: disable=unused-variable
import csv
from os import remove, environ as ENV

import boto3
from botocore.client import BaseClient
import psycopg2
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


def download_files(boto_client: boto3, bucket: str, files: list[str]) -> None:
    """Downloads a list of files from an s3 bucket

    Arguments:
        boto_client -- a boto3 s3 connection [Required]
        bucket -- a string comprising the full name of the s3 bucket [Required]
        files -- a list of stings comprising the files to download [Required]

    Returns nothing, but downloads the files to the path ./data/<filename>
    """
    if not isinstance(boto_client, BaseClient):
        raise TypeError("Required positional argument 'boto_client' must be a "
                        f"boto3 Client, not {type(boto3)}.")
    if not isinstance(bucket, str):
        raise TypeError("Required positional argument 'bucket' must be of "
                        f"type str, not {type(bucket)}.")
    if not isinstance(files, list):
        raise TypeError("Requred positional arguemnt 'files' must be of "
                        f"type list, not {type(files)}.")
    if not all(isinstance(x, str) for x in files):
        raise TypeError("All elements of positional argument 'files' "
                        "must be of type str.")
    for f in files:
        boto_client.download_file(
           bucket, f, f"data/{f}"
        )


def get_filenames(boto_client: boto3, bucket: str) -> list[str]:
    """Gets all the filenames from an s3 bucket.

    Arguments:
        boto_client -- a boto3 s3 connection [Required]
        bucket -- a string comprising the full name of the s3 bucket [Required]

    Returns:
        A list of strings representing all the files within the given bucket
    """
    if not isinstance(boto_client, BaseClient):
        raise TypeError("Required positional argument 'boto_client' must be a"
                        f" boto3 Client, not {type(boto3)}.")
    if not isinstance(bucket, str):
        raise TypeError("Required positional argument 'bucket' must be of "
                        f"type str, not {type(bucket)}.")
    raw_data = boto_client.list_objects_v2(Bucket=bucket)
    return [x["Key"] for x in raw_data["Contents"]]


def merge_csvs(csv_paths: list[str], cols: list[str], output_path: str
               ) -> None:
    """Merges a list of csvs with matching columns into a single csv.

    Arguments:
        csv_paths -- a list of strings representing the paths to the csvs you
            wish to merge. [Required]
        cols -- a list of stings representing the name of the columns to
            appear in you output. [Required]
            (n.b. these must match the columns in the existing csvs.)
        output_path -- a string representing the path you wish your output to
            be piped to. [Required]

    Returns None, but merges the named csvs into one at the output path and
        deletes the named files
    """
    with open(output_path, mode="w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=cols)
        writer.writeheader()
        for c in csv_paths:
            with open(c, mode="r", encoding="utf-8") as fp_c:
                contents = list(csv.DictReader(fp_c))
                for row in contents:
                    writer.writerow(row)
        for c in csv_paths:
            remove(c)


def load_csv_data(filepath: str) -> list[dict]:
    """Loads csv data

    Arguments:
        filepath -- a string representing the path of the file to load

    Returns:
        a list of dicts of the form {<col name>:<row value>}
    """
    with open(filepath, "r", encoding="utf-8") as fp:
        data = list(csv.DictReader(fp))
    return data


def load_id_dict(conn: psycopg2, museum_name: str) -> dict:
    """Loads id dictionaries for use in _prepare_upload_data

    Arguments:
        conn -- psycopg2 connection to your database

    Returns:
        id mapping dict, of the form:
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
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT
                        exhibition_id, public_id
                    FROM
                        exhibition
                    JOIN
                        museum
                    USING
                        (museum_id)
                    WHERE
                        museum_name = %s;""",
                (museum_name,))
    data = cur.fetchall()
    for row in data:
        row["public_id"] = str(int(row["public_id"].split('_')[-1]))
    exhibition_dict = {int(x["public_id"]): x["exhibition_id"] for x in data}
    cur.execute("SELECT rating_value, rating_id FROM rating;")
    data = cur.fetchall()
    rating_dict = {int(x["rating_value"]): x["rating_id"] for x in data}
    cur.execute("SELECT request_value, request_id from request;")
    data = cur.fetchall()
    request_dict = {int(x["request_value"]): x["request_id"] for x in data}
    id_dict = {
        "exhibition": exhibition_dict,
        "rating": rating_dict,
        "request": request_dict
    }
    return id_dict


def get_env_conn():
    load_dotenv()
    return connect(
        host=ENV["PIPELINE_TARGET_HOST"],
        user=ENV["PIPELINE_TARGET_USER"],
        password=ENV["PIPELINE_TARGET_PASSWORD"],
        dbname=ENV["PIPELINE_TARGET_DBNAME"],
        port=ENV["PIPELINE_TARGET_PORT"]
    )

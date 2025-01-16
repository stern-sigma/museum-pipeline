from os import environ as ENV
import argparse

from dotenv import load_dotenv
from boto3 import client
from psycopg2 import connect


from museum_pipeline.pipeline_logger import setup_logging
from museum_pipeline.extract import (download_files,
                                     get_filenames,
                                     merge_csvs,
                                     load_csv_data,
                                     load_id_dict)
from museum_pipeline.transform import (_prepare_upload_data,
                                       filter_strings)
from museum_pipeline.load import _upload_data


def __get_cla() -> dict:
    """Parses user arguments"""
    parser = argparse.ArgumentParser(
        prog='Sigma Lab Data Pipeline',
        description='Pipes data from an s3 bucket to and RDS DB.',
        epilog='Good Luck!'
    )
    parser.add_argument("-config_logging", action="store_true",
                        help="Enables command-line configuration of logging"
                        " handlers.", default=False)
    parser.add_argument("-stdout", choices=['true', 'false'],
                        help="Choose whether to output logs to terminal."
                        "(Default false)",
                        default='false')
    parser.add_argument("-file", choices=["true", "false"],
                        help="Choose whether to output logs to file."
                        "(Default true)",
                        default='true')
    parser.add_argument("-bucket", help="Name of the s3 bucket to connect to."
                        "(Default .env[S3_BUCKET])",
                        default=None)
    parser.add_argument("-rows", type=int, help="Number of rows to upload.",
                        default=None)
    args = parser.parse_args()
    args.stdout = args.stdout == 'true'
    args.file = args.stdout == 'true'
    return args


def _setup_handlers(args):
    """Defines logging handlers to use."""
    handlers = []
    if args.stdout:
        handlers.append("stdout")
    if args.file:
        handlers.append("file")
    return handlers


def main():
    """main function"""
    args = __get_cla()
    if args.config_logging:
        handlers = _setup_handlers(args)
        logger = setup_logging("pipeline", handlers)
    else:
        logger = setup_logging("pipeline")
    load_dotenv()
    bucket: str
    if args.bucket is not None:
        bucket = args.bucket
    else:
        bucket = ENV["S3_BUCKET"]
    boto_client = client("s3", aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                         aws_secret_access_key=ENV["AWS_SECRET_KEY"])
    logger.info("Established s3 connection.")

    files = get_filenames(boto_client, bucket)
    valid_patterns = r"lmnh_hist_data_\d+.csv"
    files = filter_strings(files, valid_patterns)
    download_files(boto_client, bucket, files)
    logger.info("Downloaded files")

    files = [f"data/{x}" for x in files]
    fieldnames = ["at", "site", "val", "type"]
    master_csv_path = "data/lmnh_hist_data.csv"
    merge_csvs(files, fieldnames, master_csv_path)
    logger.info("Merged csv")

    csv_data = load_csv_data(master_csv_path)
    with connect(
        host=ENV["PIPELINE_TARGET_HOST"],
        user=ENV["PIPELINE_TARGET_USER"],
        password=ENV["PIPELINE_TARGET_PASSWORD"],
        dbname=ENV["PIPELINE_TARGET_DBNAME"],
        port=ENV["PIPELINE_TARGET_PORT"],
    ) as conn:
        id_dict = load_id_dict(conn, "lmnh")
        payload_data = _prepare_upload_data(
                csv_data, id_dict, logger, args.rows)
        _upload_data(payload_data, conn)
    logger.info("Uploaded all files")


if __name__ == "__main__":
    main()

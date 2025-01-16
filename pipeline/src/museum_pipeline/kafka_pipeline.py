"""Library module for local kafka pipeline scripts"""
#pylint: disable=unused-variable
from os import environ as ENV
from json import loads

from dotenv import load_dotenv
from confluent_kafka import Consumer
from datetime import datetime as dt, time
from argparse import ArgumentParser

from museum_pipeline.extract import load_id_dict, get_env_conn
from museum_pipeline.pipeline_logger import setup_logging


def get_consumer_for(topics: list[str]) -> Consumer:
    load_dotenv()
    consumer = Consumer(
        {
            "bootstrap.servers": ENV["KAFKA_BOOTSTRAP_SERVERS"],
            "security.protocol": ENV["KAFKA_SECURITY_PROTOCOL"],
            "sasl.mechanisms": ENV["KAFKA_SASL_MECHANISMS"],
            "sasl.username": ENV["KAFKA_SASL_USERNAME"],
            "sasl.password": ENV["KAFKA_SASL_PASSWORD"],
            "group.id": ENV["KAFKA_GROUP_ID"],
            "auto.offset.reset": "earliest"

        }
    )
    consumer.subscribe(topics)
    return consumer


def process_val(message: dict, id_map: dict) -> None:
    """Returns message with 'val', 'type' replaced with 'value_id', 'table'"""
    if "val" not in message:
        raise KeyError("INVALID: Required key, 'val', missing.")
    val = message["val"]
    if not isinstance(val, int) or isinstance(val, bool):
        raise TypeError("INVALID: Illegal type for field 'val'.")

    if val == -1:
        if "type" not in message:
            raise KeyError("INVALID: 'type' key missing for val of -1.")
        request_type = message["type"]
        if not isinstance(request_type, int) or isinstance(request_type, bool):
            raise TypeError("INVALID: Illegal type for field 'type'.")
        request_mapping = id_map["request"]
        if request_type not in request_mapping:
            raise ValueError("INVALID: Unrecognised value for field 'type'.")
        message["value_id"] = request_mapping[request_type]
        message["table"] = "request"
        del message["type"]
    else:
        val_mapping = id_map["rating"]
        if val not in val_mapping:
            raise ValueError("INVALID: Unrecognised value for field 'val'.")
        message["value_id"] = val_mapping[val]
        message["table"] = "rating"
    del message["val"]
    return message


def process_site(message: dict, site_map: dict) -> dict:
    """Returns message, with 'site' string replaced with 'exhibition_id' int"""
    if "site" not in message:
        raise KeyError("INVALID: Required key, 'site', missing.")

    site = message["site"]
    if not site.isnumeric():
        raise ValueError("INVALID: Illegal value for field 'site'.")
    site = int(site)
    if site not in site_map:
        raise ValueError("INVALID: Unrecognised value for field 'site'.")
    message["exhibition_id"] = site_map[site]
    del message["site"]
    return message


def process_at(message: dict, start_time: time, end_time: time) -> None:
    """Returns message, with 'at' string replaced with 'evenv_at' datetime"""
    if "at" not in message:
        raise KeyError("INVALID: Required key, 'at', missing.")

    at = message["at"]
    try:
        at = dt.fromisoformat(at)
    except ValueError as e:
        raise ValueError("INVALID: Unrecognised format for field 'at'.") from e
    check_time = at.time()
    if not (start_time <= check_time <= end_time):
        raise ValueError("INVALID: You should be asleep.")
    message["event_at"] = at
    del message["at"]
    return message


def upload_message(message: dict, conn) -> None:
    """Uploads formatted Kafka messages to the database"""
    if message.get("table") not in {"request", "rating"}:
        raise ValueError("INVALID: Table name not recognised.")

    cur = conn.cursor()
    if message["table"] == "request":
        cur.execute(
            """
            INSERT INTO request_interaction
                (event_at, request_id, exhibition_id)
            VALUES
                (%(event_at)s, %(value_id)s, %(exhibition_id)s)
            ;
            """, message
        )
    else:
        cur.execute(
            """
            INSERT INTO rating_interaction
                (event_at, rating_id, exhibition_id)
            VALUES
                (%(event_at)s, %(value_id)s, %(exhibition_id)s)
            ;
            """, message
        )
    conn.commit()
    cur.close()


def get_cla():
    """Returns cli argument values"""
    parser = ArgumentParser(
        prog='Sigma Labs Data Pipeline',
        description='Pipes data from a Kafka stream to an RDS DB.'
    )
    parser.add_argument('-store', action="store_true", default=False,
                        help="Enable logging to logs/pipeline.jsonl")
    args = parser.parse_args()
    return args


def run_pipeline(museum: str, start: time, end: time) -> None:
    """Handles the core logic of the pipeline

    Parameters:
        - museum -- str, name of the museum as it appears in you database
        - start -- datetime.time, time before which interactions should be
                   disregarded
        - end -- datetime.time, time after which interactions should be
                 disregarded
    """
    args = get_cla()
    handlers: list[str]
    if args.store:
        handlers = ["file"]
    else:
        handlers = ["stdout"]
    logger = setup_logging(f"{museum}_kafka_pipeline", handlers)

    consumer = get_consumer_for([museum])
    conn = get_env_conn()
    try:
        id_dict = load_id_dict(conn, museum)
        logger.info(id_dict)

        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error() is not None:
                logger.error(msg.error().str())
                continue
            if msg.value() is None:
                continue

            try:
                msg = loads(msg.value().decode("UTF-8"))
                msg = process_val(msg, id_dict)
                msg = process_site(msg, id_dict["exhibition"])
                msg = process_at(msg, start, end)
                upload_message(msg, conn)
                logger.info(msg)
            except (KeyError, ValueError, TypeError) as e:
                logger.error(str(e))
    finally:
        conn.close()

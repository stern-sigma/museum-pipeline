#pylint: disable=unused-variable
import psycopg2
from psycopg2.extras import execute_values


def _upload_data(data: dict[str: list[tuple]], conn: psycopg2) -> None:
    """Uploads data to a database over a psycopg2 connection

    Arguments:
        data -- dict formatted as follows:
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
        conn -- psycopg2 connection
    """
    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO rating_interaction
            (event_at, rating_id, exhibition_id)
        VALUES
            %s
        ;
        """,
        data["rating"],
        "(%(event_at)s, %(value_id)s, %(exhibition_id)s)"
    )
    execute_values(
        cur,
        """
        INSERT INTO request_interaction
            (event_at, exhibition_id, request_id)
        VALUES
            %s
        ;
        """,
        data["request"],
        "(%(event_at)s, %(exhibition_id)s, %(value_id)s)"
    )
    conn.commit()




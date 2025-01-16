#pylint: skip-file
import datetime
import json
import logging
import logging.config
import logging.handlers
from typing import override

import atexit


class JSONFormatter(logging.Formatter):
    """A class for formatting log output to json"""

    def __init__(self, *, fmt_keys: dict[str: str] | None = None):
        """Initialises JSONFormatter class"""
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:

        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> str:
        always_fields = {
            "message": record.getMessage(),
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, tz=datetime.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)
        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
                }

        message.update(always_fields)

        return message


def setup_logging(logger_name: str, handlers: list[str] | None = None):
    logger = logging.getLogger(logger_name)
    with open("conf_logging.json", "r", encoding="utf-8") as fp:
        config = json.load(fp)
    if handlers is not None:
        config["handlers"]["queue_handler"]["handlers"] = handlers
    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
    return logger

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

DEFAULT_FORMAT = "[%(asctime)s] %(levelname)s | %(name)s:%(lineno)d - %(message)s"
DEFAULT_DATE_FORMAT = "%H:%M:%S"


class CustomFormatter(logging.Formatter):
    def format(self, record):
        user_id = getattr(record, "user_id", "-")
        command = getattr(record, "command", "-")
        if user_id != "-" and command != "-":
            msg = f"User {user_id} {command}: {record.getMessage()}"
            record.msg = msg
            record.args = ()
        return super().format(record)


class ContextLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        user_id = kwargs.pop("user_id", None)
        command = kwargs.pop("command", None)
        extra = kwargs.get("extra", {})
        if user_id is not None:
            extra["user_id"] = user_id
        if command is not None:
            extra["command"] = command
        if extra:
            kwargs["extra"] = extra
        return msg, kwargs


log_format = os.getenv("LOG_FORMAT", DEFAULT_FORMAT)
date_format = os.getenv("LOG_DATE_FORMAT", DEFAULT_DATE_FORMAT)

root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO")))

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(CustomFormatter(log_format, datefmt=date_format))

root_logger.handlers.clear()
root_logger.addHandler(handler)

base_logger = logging.getLogger("listify")
logger = ContextLoggerAdapter(base_logger, None)

import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "logger": record.name,
        }

        for key in (
            "method",
            "path",
            "status_code",
            "duration_ms",
            "client",
            "request_count",
            "error_count",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level=logging.INFO):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    existing_handler = next(
        (
            handler
            for handler in root_logger.handlers
            if getattr(handler, "_aviai_json_handler", False)
        ),
        None,
    )
    if existing_handler is None:
        handler = logging.StreamHandler(sys.stdout)
        handler._aviai_json_handler = True
        root_logger.addHandler(handler)
    else:
        handler = existing_handler

    handler.setFormatter(JsonFormatter())


def get_logger(name):
    configure_logging()
    return logging.getLogger(name)

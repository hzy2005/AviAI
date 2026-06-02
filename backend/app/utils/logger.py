import json
import logging
import sys
from datetime import datetime, timezone


def _parse_uvicorn_access(record):
    if record.name != "uvicorn.access" or not isinstance(record.args, tuple):
        return {}

    # Uvicorn access logs pass: client, method, path, http_version, status_code.
    if len(record.args) < 5:
        return {}

    client, method, path, _http_version, status_code = record.args[:5]
    try:
        status_code = int(status_code)
    except (TypeError, ValueError):
        pass

    return {
        "client": client,
        "method": method,
        "path": path,
        "status_code": status_code,
    }


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "logger": record.name,
        }

        payload.update(_parse_uvicorn_access(record))

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

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [handler]
        uvicorn_logger.propagate = False
        uvicorn_logger.setLevel(level)


def get_logger(name):
    configure_logging()
    return logging.getLogger(name)

# Copyright 2016-2019 Camptocamp SA
# Copyright 2017 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import functools
import logging
import os
import sys
import threading
import uuid

from odoo import http
from odoo.tools import str2bool

_logger = logging.getLogger(__name__)

try:
    from pythonjsonlogger.json import JsonFormatter
except ImportError:  # pragma: no cover
    JsonFormatter = logging.Formatter
    _logger.debug("Cannot import 'pythonjsonlogger'.")

# Same fields as Odoo's default format; ``pid`` and ``dbname`` are set on every
# record by Odoo's own LogRecord factory (odoo.netsvc.LogRecord).
LOG_FORMAT = "%(asctime)s %(pid)s %(levelname)s %(dbname)s %(name)s: %(message)s"


def is_true(value):
    return str2bool(value or "0", default=False)


class OdooJsonFormatter(JsonFormatter):
    """JSON formatter adding the current user and request id to each record.

    Attributes set on the record that are not part of the format string are
    output as extra JSON keys by python-json-logger.
    """

    def add_fields(self, log_data, record, message_dict):
        thread = threading.current_thread()
        record.uid = getattr(thread, "uid", None)
        record.request_id = getattr(thread, "request_uuid", None)
        return super().add_fields(log_data, record, message_dict)


def _patch_request_init():
    """Tag the thread handling an HTTP request with a unique request id."""
    original_init = http.Request.__init__

    @functools.wraps(original_init)
    def __init__(self, httprequest):
        original_init(self, httprequest)
        threading.current_thread().request_uuid = str(uuid.uuid4())

    http.Request.__init__ = __init__


def setup_json_logging():
    """Switch the root logger handlers to JSON output if enabled.

    Controlled by environment variables:

    * ``ODOO_LOGGING_JSON``: enable JSON logging.
    * ``ODOO_LOGGING_JSON_STDERR``: send records below WARNING to stdout and
      WARNING and above to stderr.
    """
    if not is_true(os.environ.get("ODOO_LOGGING_JSON")):
        return
    root_logger = logging.getLogger()
    if is_true(os.environ.get("ODOO_LOGGING_JSON_STDERR")):
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.addFilter(lambda record: record.levelno < logging.WARNING)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        root_logger.handlers = [stdout_handler, stderr_handler]
    formatter = OdooJsonFormatter(LOG_FORMAT)
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
    _patch_request_init()


def post_load():
    setup_json_logging()

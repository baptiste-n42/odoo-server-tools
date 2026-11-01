# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import io
import json
import logging
import os
import sys
import threading
from unittest import mock

from odoo import http
from odoo.tests import TransactionCase

from ..json_log import LOG_FORMAT, OdooJsonFormatter, setup_json_logging


class TestJsonLog(TransactionCase):
    def _setup(self, env, handlers):
        """Run setup_json_logging with the given env vars and root handlers,
        restoring the global logging and http state afterwards."""
        root_logger = logging.getLogger()
        with (
            mock.patch.dict(os.environ, env),
            mock.patch.object(root_logger, "handlers", handlers),
            mock.patch.object(http.Request, "__init__", http.Request.__init__),
        ):
            setup_json_logging()
            return list(root_logger.handlers), http.Request.__init__

    def test_formatter_output(self):
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(OdooJsonFormatter(LOG_FORMAT))
        logger = logging.getLogger("odoo.addons.logging_json.tests.formatter")
        logger.propagate = False
        logger.addHandler(handler)
        self.addCleanup(logger.removeHandler, handler)
        thread = threading.current_thread()
        with (
            mock.patch.object(thread, "uid", 42, create=True),
            mock.patch.object(thread, "request_uuid", "abc", create=True),
        ):
            logger.warning("hello %s", "world", extra={"foo": "bar"})
        data = json.loads(stream.getvalue())
        self.assertEqual(data["message"], "hello world")
        self.assertEqual(data["levelname"], "WARNING")
        self.assertEqual(data["name"], logger.name)
        self.assertEqual(data["pid"], os.getpid())
        self.assertIn("dbname", data)
        self.assertEqual(data["uid"], 42)
        self.assertEqual(data["request_id"], "abc")
        self.assertEqual(data["foo"], "bar")

    def test_disabled(self):
        handler = logging.StreamHandler(io.StringIO())
        formatter = handler.formatter
        handlers, request_init = self._setup({"ODOO_LOGGING_JSON": "0"}, [handler])
        self.assertEqual(handlers, [handler])
        self.assertIs(handler.formatter, formatter)
        self.assertIs(request_init, http.Request.__init__)

    def test_enabled(self):
        handler = logging.StreamHandler(io.StringIO())
        handlers, request_init = self._setup(
            {"ODOO_LOGGING_JSON": "1", "ODOO_LOGGING_JSON_STDERR": "0"}, [handler]
        )
        self.assertEqual(handlers, [handler])
        self.assertIsInstance(handler.formatter, OdooJsonFormatter)
        self.assertIsNot(request_init, http.Request.__init__)

    def test_split_stderr(self):
        handlers, __ = self._setup(
            {"ODOO_LOGGING_JSON": "1", "ODOO_LOGGING_JSON_STDERR": "1"},
            [logging.StreamHandler(io.StringIO())],
        )
        stdout_handler, stderr_handler = handlers
        self.assertIs(stdout_handler.stream, sys.stdout)
        self.assertIs(stderr_handler.stream, sys.stderr)
        for handler in handlers:
            self.assertIsInstance(handler.formatter, OdooJsonFormatter)
        info = logging.makeLogRecord({"levelno": logging.INFO})
        warning = logging.makeLogRecord({"levelno": logging.WARNING})
        self.assertTrue(stdout_handler.filter(info))
        self.assertFalse(stdout_handler.filter(warning))
        self.assertEqual(stderr_handler.level, logging.WARNING)

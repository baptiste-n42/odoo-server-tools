## 19.0.1.0.0

- Migration to 19.0, based on the version maintained in
  [camptocamp/odoo-cloud-platform](https://github.com/camptocamp/odoo-cloud-platform).
- Add `uid` and `request_id` to each log record.
- Add the `ODOO_LOGGING_JSON_STDERR` option.
- Remove the `ODOO_LOGGING_JSON_DEV` mode and the parsing of the cron log
  messages, which relied on log messages that no longer exist.

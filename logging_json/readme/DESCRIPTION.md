This addon allows to output the Odoo logs in JSON, so they can be parsed
by log aggregation systems (Loki, OpenSearch, Elasticsearch, ...).

Each log record contains the standard Odoo fields (`asctime`, `pid`,
`levelname`, `dbname`, `name`, `message`) plus the `uid` of the current
user and a `request_id` unique to each HTTP request, which allows to
group all the logs of a request.

Extra data passed to the logger is added as JSON keys:

``` python
_logger.info("My Message", extra={"my_extra_key_1": "value_1"})
```

The `extra` argument is part of the standard `logging` API, so this code
works with or without this module installed.

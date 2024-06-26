import logging
import requests
import json
import os


class SlackErrorHandler(logging.Handler):
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url

    def emit(self, record):
        if os.getenv("DJANGO_ENV") == "production":
            log_entry = self.format(record)
            try:
                log_entry = log_entry.replace("'", '"')
                log_entry = f"```\n{json.dumps(json.loads(log_entry), indent=4)}\n```"
            except Exception as e:
                pass
            payload = {"text": log_entry}
            requests.post(self.webhook_url, data=json.dumps(payload, indent=4))

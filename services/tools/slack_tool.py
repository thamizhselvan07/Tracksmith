import os
import logging
import requests

logger = logging.getLogger(__name__)


class SlackClient:
    def __init__(self):
        self.webhook = os.environ.get('SLACK_WEBHOOK_URL')

    def is_configured(self) -> bool:
        return bool(self.webhook)

    def post_message(self, text: str) -> bool:
        if not self.webhook:
            logger.warning('Slack webhook not configured')
            return False
        try:
            resp = requests.post(self.webhook, json={'text': text}, timeout=5)
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.exception('Slack post failed: %s', e)
            return False

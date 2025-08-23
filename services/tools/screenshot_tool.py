import os
import logging
import requests

logger = logging.getLogger(__name__)


class ScreenshotTool:
    def __init__(self):
        # expect AI_SCREENSHOT_API_KEY and AI_SCREENSHOT_ENDPOINT in env if available
        self.api_key = os.environ.get('AI_SCREENSHOT_API_KEY')
        self.endpoint = os.environ.get('AI_SCREENSHOT_ENDPOINT')

    def capture(self, company_name: str, url: str = None) -> dict:
        """Capture a screenshot via the AI Screenshot API if configured, else return a placeholder.
        Returns a dict with `image_url` or `path`.
        """
        if not url:
            return {'path': None, 'note': 'no-url'}

        if self.api_key and self.endpoint:
            try:
                resp = requests.post(self.endpoint, json={'url': url}, headers={'Authorization': f'Bearer {self.api_key}'}, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                return {'image_url': data.get('screenshot_url')}
            except Exception as e:
                logger.warning('Screenshot API failed: %s', e)
                return {'path': None, 'note': 'screenshot-failed'}

        # fallback: return a note and a placeholder path
        return {'path': f'static/images/placeholder_{company_name.lower()}.png', 'note': 'placeholder'}

import logging
from typing import Dict
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self):
        pass

    def autonomous_gather(self, company_name: str) -> Dict:
        """Attempt to find a company homepage via a web search and scrape simple metadata.

        This is intentionally simple and best-effort (no external search API used).
        """
        # naive URL guess
        url = f"https://{company_name.lower()}.com"
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else company_name
            meta_desc = ''
            md = soup.find('meta', attrs={'name': 'description'})
            if md and md.get('content'):
                meta_desc = md['content']
            return {'url': url, 'title': title, 'description': meta_desc}
        except Exception as e:
            logger.warning('Scrape failed for %s: %s', company_name, e)
            return {'url': url, 'title': company_name, 'description': ''}

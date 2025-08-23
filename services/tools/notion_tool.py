import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class NotionClient:
    def __init__(self):
        self.api_key = os.environ.get('NOTION_API_KEY')
        self.database_id = os.environ.get('NOTION_DATABASE_ID')

    def is_configured(self) -> bool:
        return bool(self.api_key and self.database_id)

    def upsert_analysis(self, companies: List[str], analysis: Dict, gathered: Dict) -> Dict:
        """Upsert a page/report into Notion. This is a minimal implementation that logs an action.

        In a real integration you'd call the Notion API with the SDK or HTTP.
        """
        logger.info('Notion upsert: companies=%s', companies)
        # For safety, do not perform any network call if not configured
        if not self.is_configured():
            logger.warning('Notion not configured; skipping upsert')
            return {'status': 'skipped'}

        # placeholder: return a pretend page id
        page_id = f"notion_page_{companies[0]}_{companies[1]}"
        logger.info('Pretend upsert succeeded, page_id=%s', page_id)
        return {'status': 'ok', 'page_id': page_id}

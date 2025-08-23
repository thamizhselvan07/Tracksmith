import os
import logging
from typing import List

from services.tools.web_scraper import WebScraper
from services.tools.screenshot_tool import ScreenshotTool
from services.tools.notion_tool import NotionClient
from services.tools.slack_tool import SlackClient
from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class SmitheryAgent:
    """A Smithery-style agent that orchestrates scraping, AI analysis, screenshots, and posting.

    Notes:
    - All external credentials are read from environment variables.
    - If an integration key is missing, the agent logs and continues using fallback behavior.
    """

    def __init__(self):
        self.scraper = WebScraper()
        self.screenshot = ScreenshotTool()
        self.notion = NotionClient()
        self.slack = SlackClient()
        self.ai = OpenAIService()

    def run_command(self, command: str) -> dict:
        """Parse a high-level command and execute the demo workflow.

        Expected demo command pattern (example):
        "Analyze our competitors Acme Corp and Globex for their latest pricing and features, then update the Notion report and notify the team on Slack."
        """
        logger.info("Agent received command: %s", command)
        steps = []

        # Very simple parsing heuristic: extract company names from the command
        # In production this should use an NLP parser; here we use a naive approach
        words = command.replace(',', '').split()
        companies = []
        for w in words:
            # crude check: capitalized words longer than 2 chars
            if w[0].isupper() and len(w) > 2 and w.lower() not in ('Analyze', 'Our', 'Our', 'for', 'their', 'latest', 'then', 'update', 'the', 'and', 'on'):
                companies.append(w)
        # fallback hard-coded demo companies if parsing fails
        if len(companies) < 2:
            companies = ['Acme', 'Globex']

        target_companies = companies[:2]
        logger.info("Parsed target companies: %s", target_companies)
        steps.append(f"Targets identified: {target_companies}")

        # Step 1: gather data for each competitor
        gathered = {}
        for c in target_companies:
            logger.info("Scraping data for %s", c)
            page_data = self.scraper.autonomous_gather(c)
            logger.info("Screenshotting %s", c)
            shot = self.screenshot.capture(c, page_data.get('url'))
            gathered[c] = {**page_data, 'screenshot': shot}
            steps.append(f"Gathered data and screenshot for {c}")

        # Step 2: run AI analysis for the pair
        try:
            logger.info("Running AI analysis")
            analysis = self.ai.analyze_competitor_data(competitor_company=target_companies[0], your_company=target_companies[1], product_domain='general', market_data=gathered)
            steps.append("AI analysis completed")
        except Exception as e:
            logger.exception("AI analysis failed")
            analysis = {
                'analysis_type': 'fallback',
                'notes': f'AI failed: {str(e)}'
            }
            steps.append("AI analysis fallback used")

        # Step 3: update Notion
        try:
            if self.notion.is_configured():
                logger.info("Updating Notion with analysis")
                notion_res = self.notion.upsert_analysis(target_companies, analysis, gathered)
                steps.append('Notion updated')
            else:
                steps.append('Notion skipped (no API key)')
        except Exception:
            logger.exception('Notion update failed')
            steps.append('Notion update failed')

        # Step 4: notify Slack
        try:
            if self.slack.is_configured():
                summary = f"Analysis for {target_companies[0]} vs {target_companies[1]} completed. See Notion for full report."
                self.slack.post_message(summary)
                steps.append('Slack notified')
            else:
                steps.append('Slack skipped (no webhook)')
        except Exception:
            logger.exception('Slack notification failed')
            steps.append('Slack notify failed')

        result = {
            'command': command,
            'targets': target_companies,
            'steps': steps,
            'analysis_preview': analysis
        }
        logger.info('Agent run complete')
        return result

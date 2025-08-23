import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
import time


class DataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def fetch_market_data(self, competitor: str, company: str, domain: str) -> dict:
        """
        Fetch real-time market data and competitive intelligence
        """
        try:
            # Simulated market data (replace with actual API calls in production)
            market_data = {
                "market_size": {
                    "value": 500000000000,
                    "currency": "USD",
                    "year": 2025
                },
                "growth_rate": {
                    "value": 12.5,
                    "period": "annual"
                },
                "market_shares": {
                    competitor: 35,
                    company: 28,
                    "others": 37
                },
                "customer_segments": [
                    {"name": "Enterprise", "share": 45},
                    {"name": "Consumer", "share": 35},
                    {"name": "SMB", "share": 20}
                ],
                "regional_distribution": {
                    "North America": 35,
                    "Europe": 25,
                    "Asia Pacific": 30,
                    "Rest of World": 10
                },
                "sentiment_analysis": {
                    competitor: {
                        "positive": 75,
                        "neutral": 15,
                        "negative": 10,
                        "mentions": 23000
                    },
                    company: {
                        "positive": 70,
                        "neutral": 20,
                        "negative": 10,
                        "mentions": 19000
                    }
                },
                "trend_indicators": {
                    "market_growth": "positive",
                    "consumer_sentiment": "stable",
                    "innovation_pace": "accelerating",
                    "competitive_intensity": "high"
                }
            }
            
            return market_data
        except Exception as e:
            logging.error(f"Error fetching market data: {str(e)}")
            return {}

    def fetch_website_data(self, url):
        """Fetch and parse website data"""
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Add timeout and error handling
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract relevant data
            data = {
                'url': url,
                'title': self._get_title(soup),
                'description': self._get_description(soup),
                'content': self._get_main_content(soup),
                'navigation': self._get_navigation(soup),
                'contact_info': self._get_contact_info(soup),
                'social_links': self._get_social_links(soup),
                'technologies': self._detect_technologies(soup, response.headers),
                'meta_data': self._get_meta_data(soup)
            }

            return data

        except requests.RequestException as e:
            logging.error(f"Error fetching website data: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error parsing website data: {str(e)}")
            return None

    def _get_title(self, soup):
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else 'No title found'

    def _get_description(self, soup):
        """Extract meta description"""
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            return desc_tag['content'].strip()

        # Fallback to first paragraph
        first_p = soup.find('p')
        return first_p.get_text().strip()[:200] + '...' if first_p else 'No description found'

    def _get_main_content(self, soup):
        """Extract main content from the page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get text content
        content = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = ' '.join(chunk for chunk in chunks if chunk)

        # Return first 2000 characters
        return content[:2000] if content else 'No content found'

    def _get_navigation(self, soup):
        """Extract navigation menu items"""
        nav_items = []
        nav_tags = soup.find_all(['nav', 'ul', 'ol'])

        for nav in nav_tags:
            links = nav.find_all('a')
            for link in links[:10]:  # Limit to first 10 links
                href = link.get('href')
                text = link.get_text().strip()
                if text and len(text) < 50:
                    nav_items.append({'text': text, 'href': href})

        return nav_items

    def _get_contact_info(self, soup):
        """Extract contact information"""
        contact_info = {}

        # Look for email addresses
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            contact_info['emails'] = list(set(emails[:3]))  # First 3 unique emails

        # Look for phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, soup.get_text())
        if phones:
            contact_info['phones'] = list(set(phones[:3]))  # First 3 unique phones

        return contact_info

    def _get_social_links(self, soup):
        """Extract social media links"""
        social_platforms = ['facebook', 'twitter', 'linkedin', 'instagram', 'youtube', 'github']
        social_links = {}

        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href'].lower()
            for platform in social_platforms:
                if platform in href and 'http' in href:
                    social_links[platform] = link['href']
                    break

        return social_links

    def _detect_technologies(self, soup, headers):
        """Detect technologies used on the website"""
        technologies = []

        # Check for common frameworks and libraries
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script['src'].lower()
            if 'react' in src:
                technologies.append('React')
            elif 'vue' in src:
                technologies.append('Vue.js')
            elif 'angular' in src:
                technologies.append('Angular')
            elif 'jquery' in src:
                technologies.append('jQuery')
            elif 'bootstrap' in src:
                technologies.append('Bootstrap')

        # Check server headers
        server = headers.get('Server', '').lower()
        if 'nginx' in server:
            technologies.append('Nginx')
        elif 'apache' in server:
            technologies.append('Apache')

        return list(set(technologies))  # Remove duplicates

    def _get_meta_data(self, soup):
        """Extract additional meta data"""
        meta_data = {}

        # Get all meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                meta_data[name] = content

        return meta_data
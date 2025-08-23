import re
from urllib.parse import urlparse


def validate_url(url):
    """Validate if the provided string is a valid URL"""
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def format_analysis_data(analysis):
    """Format analysis data for template rendering"""
    if not analysis:
        return None

    # Ensure all required sections exist
    formatted = {
        'company_overview': analysis.get('company_overview', {}),
        'products_launched': analysis.get('products_launched', []),
        'growth_metrics': analysis.get('growth_metrics', {}),
        'competitor_features': analysis.get('competitor_features', []),
        'famous_products': analysis.get('famous_products', []),
        'how_to_beat_competitor': analysis.get('how_to_beat_competitor', []),
        'advertising_opportunities': analysis.get('advertising_opportunities', []),
        'swot_analysis': analysis.get('swot_analysis', {}),
        'technical_analysis': analysis.get('technical_analysis', {}),
        'content_analysis': analysis.get('content_analysis', {})
    }

    return formatted


def sanitize_text(text):
    """Sanitize text for safe display"""
    if not isinstance(text, str):
        return str(text)

    # Remove potential HTML tags
    clean = re.sub('<.*?>', '', text)
    # Remove excessive whitespace
    clean = ' '.join(clean.split())
    return clean[:1000]  # Limit length


def format_url_display(url):
    """Format URL for display purposes"""
    if not url:
        return 'N/A'

    # Remove protocol for cleaner display
    display_url = url.replace('https://', '').replace('http://', '')
    # Remove trailing slash
    display_url = display_url.rstrip('/')

    return display_url
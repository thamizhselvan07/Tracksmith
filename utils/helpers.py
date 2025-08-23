from urllib.parse import urlparse
import json
import logging
from typing import Dict, Any
import os
from datetime import datetime

def validate_url(url: str) -> bool:
    """
    Validate if the given string is a proper URL.
    Returns True if valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
        
def generate_pdf_report(analysis_data: Dict[str, Any]) -> str:
    """
    Generate a PDF report from the analysis data.
    Returns the path to the generated PDF file.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.getcwd(), 'static', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        # Create the PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph("Competitive Analysis Report", title_style))
        story.append(Spacer(1, 12))
        
        # Add timestamp
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
        story.append(Spacer(1, 12))
        
        # Add sections
        sections = [
            ("Market Analysis", analysis_data.get("market_data", {})),
            ("SWOT Analysis", analysis_data.get("swot_analysis", {})),
            ("Strategic Recommendations", analysis_data.get("strategic_recommendations", [])),
            ("AI Insights", analysis_data.get("ai_insights", {}))
        ]
        
        for section_title, section_data in sections:
            story.append(Paragraph(section_title, styles["Heading2"]))
            story.append(Spacer(1, 12))
            
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if isinstance(value, (list, tuple)):
                        for item in value:
                            story.append(Paragraph(f"• {item}", styles["Normal"]))
                    else:
                        story.append(Paragraph(f"{key}: {value}", styles["Normal"]))
            elif isinstance(section_data, (list, tuple)):
                for item in section_data:
                    story.append(Paragraph(f"• {item}", styles["Normal"]))
            
            story.append(Spacer(1, 12))
        
        # Build the PDF
        doc.build(story)
        return filepath
        
    except Exception as e:
        logging.error(f"Error generating PDF report: {str(e)}")
        raise

def format_analysis_data(data):
    """
    Format the analysis data for display.
    Handles both dictionary and JSON string inputs.
    """
    import json
    import logging

    if not data:
        logging.warning("Empty data received in format_analysis_data")
        return {}

    try:
        # If data is a string, try to parse it as JSON
        if isinstance(data, str):
            logging.info("Parsing JSON string in format_analysis_data")
            return json.loads(data)
        
        # If data is already a dictionary, return it as is
        if isinstance(data, dict):
            logging.info("Data is already a dictionary in format_analysis_data")
            return data
        
        logging.error(f"Unexpected data type in format_analysis_data: {type(data)}")
        return {}

    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error in format_analysis_data: {str(e)}")
        return {}
    except Exception as e:
        logging.error(f"Unexpected error in format_analysis_data: {str(e)}")
        return {}

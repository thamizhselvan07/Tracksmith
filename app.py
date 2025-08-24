from flask import Flask, render_template, request, jsonify, flash, send_file
import os
import logging
from datetime import datetime
from config import Config
from services.competitor_analysis import CompetitorAnalyzer
from services.data_fetcher import DataFetcher
from services.openai_service import OpenAIService
from services.smithery_agent import SmitheryAgent
from utils.helpers import validate_url, format_analysis_data, generate_pdf_report
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
analyzer = CompetitorAnalyzer()
data_fetcher = DataFetcher()
openai_service = OpenAIService()
agent = SmitheryAgent()

# Cache for storing analysis results
analysis_cache = {}


@app.route('/')
def index():
    """Home page with input forms"""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login page (mock authentication)"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        # Mock authentication: accept any non-empty username
        if username:
            flash('Logged in successfully', 'success')
            return render_template('index.html')
        else:
            flash('Please enter a username', 'danger')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/analyze', methods=['POST'])
def analyze_competitor():
    """Analyze competitor endpoint"""
    try:
        # Log request
        app.logger.info("Starting competitor analysis")
        
        # Get form data
        competitor_company = request.form.get('competitor_company', '').strip()
        your_company = request.form.get('your_company', '').strip()
        product_domain = request.form.get('product_domain', '').strip()
        
        # Validate inputs
        if not all([competitor_company, your_company, product_domain]):
            app.logger.error("Missing required fields")
            error_msg = "Please provide all required information: competitor company, your company name, and product category."
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 400
            return render_template('error.html', error_message=error_msg)

        # Generate cache key and check cache
        cache_key = f"{competitor_company}_{your_company}_{product_domain}"
        if cache_key in analysis_cache:
            app.logger.info("Returning cached analysis")
            cached_analysis = analysis_cache[cache_key]
            return render_template(
                'analysis.html',
                analysis=cached_analysis,
                competitor_company=competitor_company,
                your_company=your_company,
                product_domain=product_domain,
                is_fallback=cached_analysis.get('is_fallback', False)
            )

        app.logger.info(f"Analyzing: Competitor={competitor_company}, Your Company={your_company}, Domain={product_domain}")

        try:
            # Get market data
            market_data = data_fetcher.fetch_market_data(competitor_company, your_company, product_domain)
            
            # Perform analysis
            analysis_result = analyzer.analyze_competitor(
                competitor_company,
                your_company,
                product_domain
            )
            
            if not analysis_result:
                raise ValueError("Analysis returned no results")

            # Use analysis_result as the main analysis object (templates expect top-level keys)
            complete_analysis = analysis_result if isinstance(analysis_result, dict) else {}

            # Ensure expected top-level keys exist and merge market data / metadata
            complete_analysis.setdefault('market_analysis', {})
            complete_analysis.setdefault('visualization_data', {})
            complete_analysis.setdefault('swot_analysis', {})
            complete_analysis['market_data'] = market_data or {}
            # Provide sentiment defaults so templates don't fail
            complete_analysis.setdefault('sentiment', complete_analysis['market_data'].get('sentiment_analysis', {}))
            complete_analysis['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            complete_analysis['is_fallback'] = analysis_result.get('is_fallback', False) if isinstance(analysis_result, dict) else True
            
            # Cache the result
            analysis_cache[cache_key] = complete_analysis
            app.logger.info("Analysis completed successfully")
            
            return render_template(
                'analysis.html',
                analysis=complete_analysis,
                competitor_company=competitor_company,
                your_company=your_company,
                product_domain=product_domain,
                is_fallback=analysis_result.get('is_fallback', False)
            )
                
        except Exception as e:
            app.logger.error(f"Analysis error: {str(e)}")
            # Get fallback analysis and present it at top-level so templates work
            fallback_analysis = analyzer._get_basic_analysis(competitor_company, your_company, product_domain)
            complete_analysis = fallback_analysis
            complete_analysis['market_data'] = market_data if 'market_data' in locals() else {}
            complete_analysis.setdefault('sentiment', complete_analysis['market_data'].get('sentiment_analysis', {}))
            complete_analysis['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            complete_analysis['is_fallback'] = True
            
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': False,
                    'error': 'An error occurred during analysis. Using fallback data.',
                    'data': complete_analysis
                }), 500
            
            return render_template(
                'analysis.html',
                analysis=complete_analysis,
                competitor_company=competitor_company,
                your_company=your_company,
                product_domain=product_domain,
                is_fallback=True
            )

    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': False,
                'error': 'An error occurred during analysis. Please try again.',
                'details': str(e)
            }), 500
        else:
            return render_template('error.html',
                error_message="An error occurred during analysis. Please try again.")


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for analysis (returns JSON)"""
    try:
        data = request.get_json()
        competitor_url = data.get('competitor_url', '').strip()
        your_company = data.get('your_company', '').strip()
        product_domain = data.get('product_domain', '').strip()

        if not competitor_url or not your_company:
            return jsonify({
                'success': False,
                'error': 'Competitor URL and your company name are required'
            }), 400

        if not validate_url(competitor_url):
            return jsonify({
                'success': False,
                'error': 'Please enter a valid URL'
            }), 400

        # Fetch and analyze
        competitor_data = data_fetcher.fetch_website_data(competitor_url)
        if not competitor_data:
            return jsonify({
                'success': False,
                'error': 'Could not fetch data from the provided URL'
            }), 400

        analysis_result = analyzer.analyze_competitor(
            competitor_company=competitor_url,
            your_company=your_company,
            product_domain=product_domain
        )

        return jsonify({
            'success': True,
            'analysis': format_analysis_data(analysis_result)
        })

    except Exception as e:
        app.logger.error(f"API Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred during analysis'
        }), 500


@app.route('/export/pdf')
def export_pdf():
    """Generate and download PDF report"""
    try:
        cache_key = request.args.get('key')
        if not cache_key or cache_key not in analysis_cache:
            return render_template('error.html',
                error_message="No analysis data found. Please perform an analysis first.")
            
        analysis_data = analysis_cache[cache_key]
        pdf_path = generate_pdf_report(analysis_data)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"competitive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
    except Exception as e:
        app.logger.error(f"PDF generation error: {str(e)}")
        return render_template('error.html',
            error_message="Error generating PDF report. Please try again.")


@app.route('/export/json')
def export_json():
    """Export analysis data as JSON"""
    try:
        cache_key = request.args.get('key')
        if not cache_key or cache_key not in analysis_cache:
            return jsonify({"error": "No analysis data found"}), 404
            
        return jsonify(analysis_cache[cache_key])
        
    except Exception as e:
        app.logger.error(f"JSON export error: {str(e)}")
        return jsonify({"error": "Error exporting data"}), 500


@app.route('/api/insights')
def get_insights():
    """Get AI-powered insights"""
    try:
        cache_key = request.args.get('key')
        if not cache_key or cache_key not in analysis_cache:
            return jsonify({"error": "No analysis data found"}), 404
            
        return jsonify(analysis_cache[cache_key].get('ai_insights', {}))
        
    except Exception as e:
        app.logger.error(f"API error: {str(e)}")
        return jsonify({"error": "Error retrieving insights"}), 500


@app.route('/api/market-data')
def get_market_data():
    """Get market data"""
    try:
        cache_key = request.args.get('key')
        if not cache_key or cache_key not in analysis_cache:
            return jsonify({"error": "No analysis data found"}), 404
            
        return jsonify(analysis_cache[cache_key].get('market_data', {}))
        
    except Exception as e:
        app.logger.error(f"API error: {str(e)}")
        return jsonify({"error": "Error retrieving market data"}), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html',
        error_message="The page you're looking for doesn't exist."), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {str(error)}")
    return render_template('error.html',
        error_message="An internal server error occurred. Our team has been notified."), 500


# For Vercel deployment
if __name__ == "__main__":
    app.run(debug=False)
else:
    # This ensures the app is available when imported
    application = app

@app.route('/run-demo')
def run_demo():
    """Trigger the Smithery agent demo workflow and return JSON summary."""
    demo_command = "Analyze our competitors Acme Corp and Globex for their latest pricing and features, then update the Notion report and notify the team on Slack."
    result = agent.run_command(demo_command)
    return jsonify(result)
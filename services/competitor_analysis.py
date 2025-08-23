import json
import logging
from .openai_service import OpenAIService

class CompetitorAnalyzer:
    def __init__(self):
        self.openai_service = OpenAIService()

    def analyze_competitor(self, competitor_company, your_company, product_domain):
        """Main method to analyze competitor company"""
        try:
            # Get basic analysis first as fallback
            basic_analysis = self._get_basic_analysis(competitor_company, your_company, product_domain)
            
            try:
                # Try to get AI-enhanced analysis (use explicit keyword args to avoid positional mismatches)
                logging.debug(f"Calling OpenAIService.analyze_competitor_data with competitor={competitor_company}, your_company={your_company}, product_domain={product_domain}")
                analysis = self.openai_service.analyze_competitor_data(
                    competitor_company=competitor_company,
                    your_company=your_company,
                    product_domain=product_domain,
                    market_data=basic_analysis
                )
                
                if isinstance(analysis, str):
                    analysis = json.loads(analysis)
                
                # Add fallback flag
                analysis['is_fallback'] = False
                
            except Exception as ai_error:
                logging.warning(f"AI analysis failed: {str(ai_error)}, using fallback data")
                basic_analysis['is_fallback'] = True
                analysis = basic_analysis
            
            if isinstance(analysis, str):
                try:
                    analysis = json.loads(analysis)
                except json.JSONDecodeError:
                    logging.warning("Could not parse AI response as JSON, using fallback")
                    analysis = basic_analysis
                    
            return analysis

        except Exception as e:
            logging.error(f"Analysis error: {str(e)}")
            return self._get_basic_analysis(competitor_company, your_company, product_domain)

    def _get_basic_analysis(self, competitor_company, your_company, product_domain):
        """Fallback basic analysis when AI is unavailable"""
        # create deterministic but varying numeric outputs based on input strings
        import hashlib

        seed_str = f"{competitor_company}|{your_company}|{product_domain}"
        seed = int(hashlib.md5(seed_str.encode('utf-8')).hexdigest()[:8], 16)

        # derive market share for competitor and your company (sum < 100)
        comp_share = 30 + (seed % 21)  # 30-50
        your_share = 20 + ((seed >> 5) % 21)  # 20-40
        others = max(0, 100 - (comp_share + your_share))

        # revenue trends: generate five points with small deterministic growth
        base_c = 80 + (seed % 50)
        base_y = 70 + ((seed >> 3) % 50)
        comp_series = [base_c + int((i * ((seed >> (i % 7)) % 12))) for i in range(5)]
        your_series = [base_y + int((i * ((seed >> ((i+2) % 11)) % 11))) for i in range(5)]

        return {
            "company_overview": {
                "name": competitor_company,
                "industry": product_domain,
                "target_audience": "General audience"
            },
            "market_analysis": {
                "market_share": {
                    competitor_company: f"{comp_share}%",
                    your_company: f"{your_share}%",
                    "others": f"{others}%"
                },
                "revenue_trends": {
                    "labels": ["2020", "2021", "2022", "2023", "2024"],
                    "datasets": [
                        {
                            "label": competitor_company,
                            "data": comp_series
                        },
                        {
                            "label": your_company,
                            "data": your_series
                        }
                    ]
                }
            },
            "visualization_data": {
                "market_share_data": {
                    "labels": [competitor_company, your_company, "Others"],
                    "values": [comp_share, your_share, others]
                },
                "product_comparison": {
                    "categories": ["Innovation", "Price", "Quality", "Market Share", "Brand Value"],
                    "datasets": [
                        {
                            "label": competitor_company,
                            "data": [
                                7 + ((seed >> 2) % 4),
                                6 + ((seed >> 4) % 4),
                                7 + ((seed >> 6) % 4),
                                6 + ((seed >> 8) % 4),
                                7 + ((seed >> 10) % 4)
                            ]
                        },
                        {
                            "label": your_company,
                            "data": [
                                6 + ((seed >> 3) % 4),
                                7 + ((seed >> 5) % 4),
                                6 + ((seed >> 7) % 4),
                                7 + ((seed >> 9) % 4),
                                6 + ((seed >> 11) % 4)
                            ]
                        }
                    ]
                }
            },
            "swot_analysis": {
                "strengths": [
                    f"Strong market presence in {product_domain}",
                    "Clear brand messaging"
                ],
                "weaknesses": [
                    "Limited data available",
                    "Need deeper market research"
                ],
                "opportunities": [
                    "Market expansion",
                    "Product innovation"
                ],
                "threats": [
                    "Market competition",
                    "Technology changes"
                ]
            },
            "is_fallback": True
        }

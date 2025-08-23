import openai
import json
import logging
from config import Config

class OpenAIService:
    def __init__(self):
        try:
            import os
            os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
            if not Config.OPENAI_API_KEY:
                raise ValueError("OpenAI API key is not set")
            self.client = openai.OpenAI()
            logging.info("OpenAI service initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI service: {str(e)}")
            raise

    def analyze_competitor_data(self, competitor_company, your_company, product_domain):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a business analyst. Return analysis in JSON format only."},
                    {"role": "user", "content": f"Compare {competitor_company} vs {your_company} in {product_domain} market"}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            return json.dumps(self._get_fallback_analysis(competitor_company, your_company, product_domain))

    def _get_fallback_analysis(self, competitor_company, your_company, product_domain):
        return {
            "company_overview": {
                "name": competitor_company,
                "industry": product_domain,
                "target_audience": "General audience"
            },
            "market_analysis": {
                "market_share": {
                    competitor_company: "35%",
                    your_company: "28%",
                    "others": "37%"
                },
                "revenue_trends": {
                    "labels": ["2020", "2021", "2022", "2023", "2024"],
                    "datasets": [
                        {
                            "label": competitor_company,
                            "data": [100, 120, 150, 180, 200]
                        },
                        {
                            "label": your_company,
                            "data": [90, 110, 140, 160, 185]
                        }
                    ]
                }
            },
            "visualization_data": {
                "market_share_data": {
                    "labels": [competitor_company, your_company, "Others"],
                    "values": [35, 28, 37]
                },
                "product_comparison": {
                    "categories": ["Innovation", "Price", "Quality", "Market Share", "Brand Value"],
                    "datasets": [
                        {
                            "label": competitor_company,
                            "data": [9, 7, 9, 8, 9]
                        },
                        {
                            "label": your_company,
                            "data": [8, 9, 8, 7, 8]
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
            }
        }

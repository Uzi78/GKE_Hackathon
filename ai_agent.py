# ai_agent.py - Complete AI Agent Implementation for Travel Shopping Chatbot
"""
AI Agent with Gemini integration for Travel & Culture-Aware Shopping Chatbot
Handles intent parsing, cultural context, and response generation
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import re

try:
    from google.cloud import aiplatform
    from vertexai.generative_models import GenerativeModel, Part
    import vertexai
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logging.warning("Vertex AI not available. Install with: pip install google-cloud-aiplatform")

from cultural_data import CulturalDataManager

class TravelShoppingAgent:
    """
    Main AI Agent that orchestrates all AI-powered functionality
    """
    
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location
        
        if VERTEX_AI_AVAILABLE and self.project_id:
            try:
                credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if credentials_path and os.path.exists(credentials_path):
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                
                vertexai.init(project=self.project_id, location=self.location)
                
                # Try different model names
                model_names = [
                    "gemini-1.5-flash-002", 
                    "gemini-pro",
                    "gemini-1.0-pro-001"
                ]
                
                self.model = None
                for model_name in model_names:
                    try:
                        self.model = GenerativeModel(model_name)
                        self.logger.info(f"Successfully initialized model: {model_name}")
                        break
                    except Exception as e:
                        self.logger.warning(f"Failed to load {model_name}: {e}")
                        continue
                
                if self.model:
                    self.ai_available = True
                    self.logger.info(f"Vertex AI initialized for project: {self.project_id}")
                else:
                    self.ai_available = False
                    self.logger.error("No compatible Gemini model found")
                    
            except Exception as e:
                self.logger.error(f"Failed to initialize Vertex AI: {e}")
                self.ai_available = False
        else:
            self.ai_available = False
            self.logger.warning("Using mock AI - Vertex AI not configured")
        
        self.cultural_manager = CulturalDataManager()
        self.logger.info(f"TravelShoppingAgent initialized (AI: {self.ai_available})")
    
    def parse_intent(self, query: str) -> Dict[str, Any]:
        """
        Parse user query to extract travel intent using Gemini AI
        """
        if not self.ai_available:
            return self._mock_parse_intent(query)
        
        try:
            prompt = f"""
            Analyze this travel shopping query and extract structured information.
            
            Query: "{query}"
            
            Extract and return ONLY a JSON object with these exact fields:
            {{
                "destination": "main destination mentioned (city or country)",
                "city": "specific city mentioned or null if not specified",
                "country": "country mentioned or inferred from city, or null",
                "dates": "time period mentioned or 'unspecified'",
                "category": "main product category (clothing/accessories/gifts/electronics/beauty/home)",
                "travel_purpose": "vacation/business/visiting_family/cultural_event/other",
                "budget_mentioned": true/false,
                "urgency": "immediate/soon/flexible",
                "cultural_event": "specific festival/event mentioned or null",
                "weather_concern": true/false,
                "confidence": 0.0-1.0
            }}
            
            Examples:
            - "What to pack for Karachi Pakistan in January?" → {{"destination": "Karachi Pakistan", "city": "Karachi", "country": "Pakistan", "dates": "January", "category": "clothing", "weather_concern": true}}
            - "Eid gifts for Dubai trip" → {{"destination": "Dubai", "city": "Dubai", "country": "UAE", "category": "gifts", "cultural_event": "Eid"}}
            - "Summer clothes for Turkey" → {{"destination": "Turkey", "city": null, "country": "Turkey", "dates": "summer", "category": "clothing"}}
            
            Return ONLY the JSON, no other text.
            """
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                intent_data = json.loads(json_match.group())
            else:
                intent_data = json.loads(response_text)
            
            # Validate and enrich
            intent_data = self._validate_intent_data(intent_data, query)
            
            self.logger.info(f"Successfully parsed intent with AI: {intent_data.get('destination')} - {intent_data.get('category')}")
            return intent_data
            
        except Exception as e:
            self.logger.error(f"AI intent parsing failed: {e}")
            return self._mock_parse_intent(query)
    
    def get_cultural_context(self, destination: str, dates: str = None, cultural_event: str = None, city: str = None) -> Dict[str, Any]:
        """
        Get AI-powered cultural context with MCP grounding
        """
        if not self.ai_available:
            return self._mock_cultural_context(destination, city)
        
        try:
            # Get grounding data from cultural manager with city information
            base_cultural_data = self.cultural_manager.get_cultural_data(destination, dates, city)
            
            prompt = f"""
            Provide cultural context for travelers visiting {destination}{f' ({city})' if city else ''} in {dates or 'unspecified time'}.
            
            Base cultural data: {json.dumps(base_cultural_data, indent=2)}
            
            Consider these aspects and return a JSON object:
            {{
                "clothing_norms": {{
                    "general": "overall dress code expectations",
                    "religious_sites": "specific requirements for religious places",
                    "business": "business attire expectations",
                    "casual": "everyday wear guidelines"
                }},
                "cultural_events": [
                    {{
                        "name": "event name",
                        "dates": "when it occurs",
                        "significance": "why it matters",
                        "shopping_relevance": "gift ideas or clothing needs"
                    }}
                ],
                "seasonal_considerations": {{
                    "weather_impact": "how weather affects clothing choices",
                    "local_preferences": "what locals typically wear this season"
                }},
                "shopping_etiquette": {{
                    "bargaining": "is bargaining expected/acceptable",
                    "gift_giving": "cultural norms around gifts",
                    "taboos": ["items to avoid"]
                }},
                "sensitivity_flags": ["important cultural considerations"]
            }}
            
            Focus on practical, respectful advice for travelers. Be inclusive and avoid stereotypes.
            Return ONLY the JSON, no other text.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            response_text = response.text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                cultural_context = json.loads(json_match.group())
            else:
                cultural_context = json.loads(response_text)
            
            # Apply MCP filters
            cultural_context = self.cultural_manager.apply_mcp_filters(cultural_context, destination)
            
            self.logger.info(f"Generated cultural context for {destination}")
            return cultural_context
            
        except Exception as e:
            self.logger.error(f"Cultural context AI generation failed: {e}")
            return self._mock_cultural_context(destination)
    
    def generate_response(self, original_query: str, intent_data: Dict, 
                         context_data: Dict, products: List[Dict]) -> Dict[str, Any]:
        """
        Generate final AI-powered response with cultural storytelling
        """
        if not self.ai_available:
            return self._mock_generate_response(original_query, intent_data, context_data, products)
        
        try:
            destination = intent_data.get('destination', 'your destination')
            category = intent_data.get('category', 'items')
            
            # Prepare context summary
            weather_summary = context_data.get('weather', {}).get('summary', '')
            cultural_norms = context_data.get('cultural', {}).get('clothing_norms', {}).get('general', '')
            
            prompt = f"""
            You are a knowledgeable, culturally-sensitive travel shopping assistant. 
            Create a helpful response for this traveler's query.
            
            Original Query: "{original_query}"
            
            Travel Context:
            - Destination: {destination}
            - Category: {category}
            - Weather: {weather_summary}
            - Cultural Context: {json.dumps(context_data.get('cultural', {}), indent=2)}
            
            Available Products: {json.dumps(products, indent=2)}
            
            Create a response with this structure:
            {{
                "greeting": "Warm, personalized greeting addressing their travel plans",
                "context_explanation": "2-3 sentences explaining weather and cultural considerations",
                "product_recommendations": [
                    {{
                        "product_id": "from products list",
                        "reason": "detailed explanation why this item is perfect for their trip",
                        "cultural_relevance": "how it respects local customs or enhances experience"
                    }}
                ],
                "additional_tips": [
                    "practical travel advice related to their destination"
                ],
                "closing": "encouraging closing with offer to help more"
            }}
            
            Make it conversational, informative, and culturally respectful. 
            Use specific details from the products and cultural context.
            Return ONLY the JSON, no other text.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            response_text = response.text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                ai_response = json.loads(json_match.group())
            else:
                ai_response = json.loads(response_text)
            
            # Create final formatted response
            return {
                "message": ai_response.get("greeting", "Hello! I'd be happy to help with your travel shopping."),
                "explanation": ai_response.get("context_explanation", "Based on your travel plans, here are my recommendations."),
                "products": products,
                "product_insights": ai_response.get("product_recommendations", []),
                "travel_tips": ai_response.get("additional_tips", []),
                "context": context_data,
                "metadata": {
                    "query_processed_at": datetime.now().isoformat(),
                    "intent": intent_data,
                    "products_count": len(products),
                    "ai_generated": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"AI response generation failed: {e}")
            return self._mock_generate_response(original_query, intent_data, context_data, products)
    
    def _validate_intent_data(self, intent_data: Dict, original_query: str) -> Dict:
        """Validate and enrich intent data"""
        # Set defaults for missing fields
        defaults = {
            "destination": "unspecified",
            "city": None,
            "country": None,
            "dates": "unspecified", 
            "category": "clothing",
            "travel_purpose": "vacation",
            "budget_mentioned": False,
            "urgency": "flexible",
            "cultural_event": None,
            "weather_concern": False,
            "confidence": 0.5,
            "original_query": original_query,
            "parsed_successfully": True
        }
        
        for key, default_value in defaults.items():
            if key not in intent_data:
                intent_data[key] = default_value
        
        return intent_data
    
    # Mock implementations for fallback
    def _mock_parse_intent(self, query: str) -> Dict:
        """Enhanced mock implementation with generic destination support"""
        query_lower = query.lower()
        
        # Enhanced destination detection with city/country separation
        destination = "unspecified"
        city = None
        country = None
        
        # First check predefined destinations with city/country mapping
        predefined_destinations = {
            'karachi': {'city': 'Karachi', 'country': 'Pakistan'},
            'lahore': {'city': 'Lahore', 'country': 'Pakistan'},
            'islamabad': {'city': 'Islamabad', 'country': 'Pakistan'},
            'skardu': {'city': 'Skardu', 'country': 'Pakistan'},
            'istanbul': {'city': 'Istanbul', 'country': 'Turkey'},
            'ankara': {'city': 'Ankara', 'country': 'Turkey'},
            'tokyo': {'city': 'Tokyo', 'country': 'Japan'},
            'kyoto': {'city': 'Kyoto', 'country': 'Japan'},
            'amsterdam': {'city': 'Amsterdam', 'country': 'Netherlands'},
            'rotterdam': {'city': 'Rotterdam', 'country': 'Netherlands'},
            'dubai': {'city': 'Dubai', 'country': 'UAE'},
            'mumbai': {'city': 'Mumbai', 'country': 'India'},
            'delhi': {'city': 'Delhi', 'country': 'India'}
        }
        
        for key, location_info in predefined_destinations.items():
            if key in query_lower:
                city = location_info['city']
                country = location_info['country']
                destination = f"{city}, {country}"
                break
        
        # If not found in predefined, try to extract country and city separately
        if not city and not country:
            # Country detection
            countries = ['pakistan', 'turkey', 'japan', 'netherlands', 'india', 'uae', 'china', 'korea']
            for c in countries:
                if c in query_lower:
                    country = c.title()
                    break
            
            # City detection - look for capitalized words that might be cities
            words = query.split()
            for word in words:
                if word[0].isupper() and len(word) > 2 and word.lower() not in ['what', 'should', 'wear', 'going', 'traveling', 'trip', 'pack', 'buy']:
                    if not city and word.lower() != country.lower():
                        city = word
                        break
            
            if country and city:
                destination = f"{city}, {country}"
            elif country:
                destination = country
            elif city:
                destination = city
        
        # Category detection
        category = "clothing"  # default
        if any(word in query_lower for word in ['gift', 'present', 'souvenir']):
            category = "gifts"
        elif any(word in query_lower for word in ['accessory', 'accessories', 'watch', 'jewelry']):
            category = "accessories"
        elif any(word in query_lower for word in ['electronics', 'gadget', 'phone']):
            category = "electronics"
        
        # Date detection
        dates = "unspecified"
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december']
        for month in months:
            if month in query_lower:
                dates = month.capitalize()
                break
        
        return {
            "destination": destination,
            "city": city,
            "country": country,
            "dates": dates,
            "category": category,
            "travel_purpose": "vacation",
            "budget_mentioned": any(word in query_lower for word in ['budget', 'cheap', 'expensive', '$']),
            "urgency": "immediate" if any(word in query_lower for word in ['urgent', 'asap', 'quick']) else "flexible",
            "cultural_event": "Eid" if 'eid' in query_lower else None,
            "weather_concern": any(word in query_lower for word in ['weather', 'cold', 'hot', 'rain', 'pack']),
            "confidence": 0.7,
            "original_query": query,
            "parsed_successfully": True,
            "mock_response": True
        }
    
    def _mock_cultural_context(self, destination: str, city: str = None) -> Dict:
        """Mock cultural context for fallback with regional support"""
        return self.cultural_manager.get_cultural_data(destination, city=city)
    
    def _mock_generate_response(self, query: str, intent: Dict, context: Dict, products: List) -> Dict:
        """Mock response generation for fallback"""
        destination = intent.get('destination', 'your destination')
        
        return {
            "message": f"Great question about traveling to {destination}! I've found some recommendations for you.",
            "explanation": f"Based on your trip to {destination}, considering the local weather and cultural preferences, here are my suggestions:",
            "products": products,
            "product_insights": [
                {
                    "product_id": products[0].get('id', 'N/A') if products else 'N/A',
                    "reason": "This item is versatile and suitable for your travel needs",
                    "cultural_relevance": "Appropriate for the local dress customs"
                }
            ],
            "travel_tips": [
                "Pack layers for changing weather conditions",
                "Research local customs before your trip",
                "Keep copies of important documents"
            ],
            "context": context,
            "metadata": {
                "query_processed_at": datetime.now().isoformat(),
                "intent": intent,
                "products_count": len(products),
                "ai_generated": False,
                "mock_response": True
            }
        }
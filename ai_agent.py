# ai_agent.py - Fixed version with proper seasonal handling
"""
AI Agent with Gemini integration for Travel & Culture-Aware Shopping Chatbot
FIXED: Proper seasonal context parsing and climate-appropriate recommendations
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
    FIXED: Better seasonal context parsing and climate filtering
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
                
                model_names = [
                    "gemini-2.5-pro",
                    "gemini-2.5-flash",
                    "gemini-2.5-flash-lite",
                    "gemini-2.0-flash-001"
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
        Parse user query to extract travel intent - FIXED seasonal detection
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
                "season": "winter/summer/spring/autumn or specific month if mentioned",
                "dates": "time period mentioned or 'unspecified'",
                "category": "main product category (clothing/accessories/gifts/electronics/beauty/home)",
                "travel_purpose": "vacation/business/visiting_family/cultural_event/other",
                "budget_mentioned": true/false,
                "urgency": "immediate/soon/flexible",
                "cultural_event": "specific festival/event mentioned or null",
                "weather_concern": true/false,
                "climate_keywords": ["keywords like hot, cold, warm, cool, winter, summer"],
                "confidence": 0.0-1.0
            }}
            
            Examples:
            - "What to pack for Pakistan in winters?" → {{"destination": "Pakistan", "country": "Pakistan", "season": "winter", "category": "clothing", "weather_concern": true, "climate_keywords": ["winter", "cold"]}}
            - "Summer clothes for Turkey" → {{"destination": "Turkey", "country": "Turkey", "season": "summer", "category": "clothing", "climate_keywords": ["summer", "hot"]}}
            - "What should I pack for Turkey?" → {{"destination": "Turkey", "country": "Turkey", "season": "unspecified", "category": "clothing"}}
            
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
            
            self.logger.info(f"Successfully parsed intent: {intent_data.get('destination')} - {intent_data.get('season')} - {intent_data.get('category')}")
            return intent_data
            
        except Exception as e:
            self.logger.error(f"AI intent parsing failed: {e}")
            return self._mock_parse_intent(query)
    
    def get_cultural_context(self, destination: str, season: str = None, dates: str = None, 
                           cultural_event: str = None, city: str = None) -> Dict[str, Any]:
        """
        Get AI-powered cultural context with seasonal considerations
        """
        if not self.ai_available:
            return self._mock_cultural_context(destination, city, season)
        
        try:
            # Get grounding data from cultural manager with seasonal information
            base_cultural_data = self.cultural_manager.get_cultural_data(destination, dates, city)
            
            # Get seasonal climate data if available
            seasonal_climate = None
            if city and season:
                seasonal_climate = self.cultural_manager.get_regional_climate_data(destination, city, season)
            
            prompt = f"""
            Provide cultural context for travelers visiting {destination}{f' ({city})' if city else ''} in {season or 'unspecified season'}.
            
            Base cultural data: {json.dumps(base_cultural_data, indent=2)}
            Seasonal climate data: {json.dumps(seasonal_climate, indent=2) if seasonal_climate else 'Not available'}
            
            Consider these aspects and return a JSON object:
            {{
                "clothing_norms": {{
                    "general": "overall dress code expectations",
                    "religious_sites": "specific requirements for religious places",
                    "business": "business attire expectations",
                    "casual": "everyday wear guidelines",
                    "seasonal_considerations": "how season affects clothing choices"
                }},
                "cultural_events": [
                    {{
                        "name": "event name",
                        "dates": "when it occurs",
                        "significance": "why it matters",
                        "shopping_relevance": "gift ideas or clothing needs"
                    }}
                ],
                "seasonal_climate": {{
                    "temperature_range": "expected temperature range",
                    "weather_description": "weather conditions",
                    "clothing_recommendations": "season-appropriate clothing advice"
                }},
                "shopping_etiquette": {{
                    "bargaining": "is bargaining expected/acceptable",
                    "gift_giving": "cultural norms around gifts",
                    "taboos": ["items to avoid"]
                }},
                "sensitivity_flags": ["important cultural considerations"]
            }}
            
            Focus on practical, respectful advice for travelers. Include seasonal weather considerations.
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
            
            self.logger.info(f"Generated cultural context for {destination} in {season}")
            return cultural_context
            
        except Exception as e:
            self.logger.error(f"Cultural context AI generation failed: {e}")
            return self._mock_cultural_context(destination, city, season)
    
    def generate_response(self, original_query: str, intent_data: Dict, 
                         context_data: Dict, products: List[Dict]) -> Dict[str, Any]:
        """
        Generate final AI-powered response with seasonal storytelling
        """
        if not self.ai_available:
            return self._mock_generate_response(original_query, intent_data, context_data, products)
        
        try:
            destination = intent_data.get('destination', 'your destination')
            category = intent_data.get('category', 'items')
            season = intent_data.get('season', 'unspecified')
            climate_keywords = intent_data.get('climate_keywords', [])
            
            # Prepare seasonal context
            seasonal_context = ""
            if season and season != 'unspecified':
                seasonal_context = f"for {season} season"
            elif climate_keywords:
                seasonal_context = f"considering {', '.join(climate_keywords)} conditions"
            
            # Get seasonal climate data
            seasonal_climate = context_data.get('seasonal_climate', {})
            
            prompt = f"""
            You are a knowledgeable, culturally-sensitive travel shopping assistant specializing in seasonal recommendations.
            Create a helpful response for this traveler's query.
            
            Original Query: "{original_query}"
            
            Travel Context:
            - Destination: {destination}
            - Season: {season}
            - Climate Keywords: {climate_keywords}
            - Category: {category}
            - Seasonal Climate: {json.dumps(seasonal_climate, indent=2)}
            - Cultural Context: {json.dumps(context_data.get('cultural', {}), indent=2)}
            
            Available Products: {json.dumps(products[:6], indent=2)}
            
            Create a response with this structure:
            {{
                "greeting": "Warm, personalized greeting mentioning their destination and season",
                "seasonal_context": "2-3 sentences explaining seasonal weather and climate considerations",
                "context_explanation": "Cultural considerations and local customs",
                "product_recommendations": [
                    {{
                        "product_id": "from products list",
                        "reason": "detailed explanation why this item is perfect for the season/climate",
                        "seasonal_relevance": "how it addresses specific seasonal needs",
                        "cultural_relevance": "how it respects local customs"
                    }}
                ],
                "additional_tips": [
                    "practical seasonal travel advice for their destination"
                ],
                "closing": "encouraging closing with seasonal-specific advice"
            }}
            
            Make it conversational, informative, and focused on seasonal appropriateness.
            Use specific seasonal details and climate considerations.
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
                "message": ai_response.get("greeting", f"Great question about traveling to {destination}!"),
                "seasonal_context": ai_response.get("seasonal_context", ""),
                "explanation": ai_response.get("context_explanation", "Based on your travel plans, here are my recommendations."),
                "products": products,
                "product_insights": ai_response.get("product_recommendations", []),
                "travel_tips": ai_response.get("additional_tips", []),
                "context": context_data,
                "metadata": {
                    "query_processed_at": datetime.now().isoformat(),
                    "intent": intent_data,
                    "products_count": len(products),
                    "ai_generated": True,
                    "seasonal_filtering_applied": season != 'unspecified'
                }
            }
            
        except Exception as e:
            self.logger.error(f"AI response generation failed: {e}")
            return self._mock_generate_response(original_query, intent_data, context_data, products)
    
    def _validate_intent_data(self, intent_data: Dict, original_query: str) -> Dict:
        """Validate and enrich intent data with better seasonal detection"""
        # Set defaults for missing fields
        defaults = {
            "destination": "unspecified",
            "city": None,
            "country": None,
            "season": "unspecified",
            "dates": "unspecified", 
            "category": "clothing",
            "travel_purpose": "vacation",
            "budget_mentioned": False,
            "urgency": "flexible",
            "cultural_event": None,
            "weather_concern": False,
            "climate_keywords": [],
            "confidence": 0.5,
            "original_query": original_query,
            "parsed_successfully": True
        }
        
        for key, default_value in defaults.items():
            if key not in intent_data:
                intent_data[key] = default_value
        
        # Enhanced seasonal detection from query text
        query_lower = original_query.lower()
        
        # Detect seasons and climate keywords
        if intent_data.get('season') == 'unspecified':
            if any(word in query_lower for word in ['winter', 'winters', 'cold']):
                intent_data['season'] = 'winter'
                intent_data['climate_keywords'] = ['winter', 'cold']
            elif any(word in query_lower for word in ['summer', 'hot', 'warm']):
                intent_data['season'] = 'summer'
                intent_data['climate_keywords'] = ['summer', 'hot']
            elif any(word in query_lower for word in ['spring']):
                intent_data['season'] = 'spring'
                intent_data['climate_keywords'] = ['spring', 'mild']
            elif any(word in query_lower for word in ['autumn', 'fall']):
                intent_data['season'] = 'autumn'
                intent_data['climate_keywords'] = ['autumn', 'cool']
        
        # Detect specific months
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december']
        for month in months:
            if month in query_lower:
                intent_data['dates'] = month.capitalize()
                # Map months to seasons
                if month in ['december', 'january', 'february']:
                    intent_data['season'] = 'winter'
                    intent_data['climate_keywords'] = ['winter', 'cold']
                elif month in ['march', 'april', 'may']:
                    intent_data['season'] = 'spring'
                    intent_data['climate_keywords'] = ['spring', 'mild']
                elif month in ['june', 'july', 'august']:
                    intent_data['season'] = 'summer'
                    intent_data['climate_keywords'] = ['summer', 'hot']
                elif month in ['september', 'october', 'november']:
                    intent_data['season'] = 'autumn'
                    intent_data['climate_keywords'] = ['autumn', 'cool']
                break
        
        return intent_data
    
    # Enhanced mock implementations for fallback
    def _mock_parse_intent(self, query: str) -> Dict:
        """Enhanced mock implementation with better seasonal detection"""
        query_lower = query.lower()
        
        # Enhanced destination detection
        destination = "unspecified"
        city = None
        country = None
        
        predefined_destinations = {
            'karachi': {'city': 'Karachi', 'country': 'Pakistan'},
            'lahore': {'city': 'Lahore', 'country': 'Pakistan'},
            'islamabad': {'city': 'Islamabad', 'country': 'Pakistan'},
            'skardu': {'city': 'Skardu', 'country': 'Pakistan'},
            'istanbul': {'city': 'Istanbul', 'country': 'Turkey'},
            'ankara': {'city': 'Ankara', 'country': 'Turkey'},
            'tokyo': {'city': 'Tokyo', 'country': 'Japan'},
            'kyoto': {'city': 'Kyoto', 'country': 'Japan'},
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
        
        # If not found in predefined, try country names
        if not city and not country:
            countries = ['pakistan', 'turkey', 'japan', 'netherlands', 'india', 'uae', 'china', 'korea']
            for c in countries:
                if c in query_lower:
                    country = c.title()
                    destination = country
                    break
        
        # Enhanced seasonal detection
        season = "unspecified"
        climate_keywords = []
        weather_concern = False
        
        if any(word in query_lower for word in ['winter', 'winters', 'cold']):
            season = 'winter'
            climate_keywords = ['winter', 'cold']
            weather_concern = True
        elif any(word in query_lower for word in ['summer', 'hot', 'warm']):
            season = 'summer'
            climate_keywords = ['summer', 'hot']
            weather_concern = True
        elif any(word in query_lower for word in ['spring']):
            season = 'spring'
            climate_keywords = ['spring', 'mild']
            weather_concern = True
        elif any(word in query_lower for word in ['autumn', 'fall']):
            season = 'autumn'
            climate_keywords = ['autumn', 'cool']
            weather_concern = True
        
        # Month detection
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december']
        dates = "unspecified"
        for month in months:
            if month in query_lower:
                dates = month.capitalize()
                weather_concern = True
                # Map months to seasons if not already detected
                if season == "unspecified":
                    if month in ['december', 'january', 'february']:
                        season = 'winter'
                        climate_keywords = ['winter', 'cold']
                    elif month in ['march', 'april', 'may']:
                        season = 'spring'
                        climate_keywords = ['spring', 'mild']
                    elif month in ['june', 'july', 'august']:
                        season = 'summer'
                        climate_keywords = ['summer', 'hot']
                    elif month in ['september', 'october', 'november']:
                        season = 'autumn'
                        climate_keywords = ['autumn', 'cool']
                break
        
        # Category detection
        category = "clothing"  # default
        if any(word in query_lower for word in ['gift', 'present', 'souvenir']):
            category = "gifts"
        elif any(word in query_lower for word in ['accessory', 'accessories', 'watch', 'jewelry']):
            category = "accessories"
        elif any(word in query_lower for word in ['electronics', 'gadget', 'phone']):
            category = "electronics"
        
        return {
            "destination": destination,
            "city": city,
            "country": country,
            "season": season,
            "dates": dates,
            "category": category,
            "travel_purpose": "vacation",
            "budget_mentioned": any(word in query_lower for word in ['budget', 'cheap', 'expensive', '$']),
            "urgency": "immediate" if any(word in query_lower for word in ['urgent', 'asap', 'quick']) else "flexible",
            "cultural_event": "Eid" if 'eid' in query_lower else None,
            "weather_concern": weather_concern,
            "climate_keywords": climate_keywords,
            "confidence": 0.7,
            "original_query": query,
            "parsed_successfully": True,
            "mock_response": True
        }
    
    def _mock_cultural_context(self, destination: str, city: str = None, season: str = None) -> Dict:
        """Mock cultural context with seasonal considerations"""
        base_context = self.cultural_manager.get_cultural_data(destination, season, city)
        
        # Add seasonal climate data if available
        seasonal_climate = {}
        if city and season:
            climate_data = self.cultural_manager.get_regional_climate_data(destination, city, season)
            if climate_data:
                seasonal_climate = {
                    "temperature_range": climate_data.get("current_month_weather", {}).get("temp_range", "Variable"),
                    "weather_description": climate_data.get("current_month_weather", {}).get("description", "Seasonal weather"),
                    "clothing_recommendations": climate_data.get("current_month_weather", {}).get("clothing", "Season-appropriate clothing")
                }
        
        base_context["seasonal_climate"] = seasonal_climate
        return base_context
    
    def _mock_generate_response(self, query: str, intent: Dict, context: Dict, products: List) -> Dict:
        """Mock response generation with seasonal context"""
        destination = intent.get('destination', 'your destination')
        season = intent.get('season', 'unspecified')
        climate_keywords = intent.get('climate_keywords', [])
        
        seasonal_context = ""
        if season != 'unspecified':
            seasonal_context = f"Traveling to {destination} in {season} requires specific clothing considerations."
        elif climate_keywords:
            seasonal_context = f"Given the {', '.join(climate_keywords)} conditions in {destination}, proper clothing selection is important."
        
        return {
            "message": f"Perfect timing to plan for {destination}! Let me help you pack appropriately.",
            "seasonal_context": seasonal_context,
            "explanation": f"Based on your {season} trip to {destination}, considering local customs and climate, here are my recommendations:",
            "products": products,
            "product_insights": [
                {
                    "product_id": products[0].get('id', 'N/A') if products else 'N/A',
                    "reason": f"This item is ideal for {season} weather conditions",
                    "seasonal_relevance": f"Perfectly suited for {season} temperatures and activities",
                    "cultural_relevance": "Appropriate for local dress customs"
                }
            ],
            "travel_tips": [
                f"Layer clothing for {season} temperature variations" if season != 'unspecified' else "Pack versatile layers",
                "Research local customs before your trip",
                "Keep important documents accessible"
            ],
            "context": context,
            "metadata": {
                "query_processed_at": datetime.now().isoformat(),
                "intent": intent,
                "products_count": len(products),
                "ai_generated": False,
                "mock_response": True,
                "seasonal_filtering_applied": season != 'unspecified'
            }
        }
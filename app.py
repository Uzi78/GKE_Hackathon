# app.py - Fixed orchestrator with proper seasonal product filtering
"""
Travel & Culture-Aware Shopping Chatbot Backend - FIXED VERSION
Proper seasonal context handling and climate-appropriate product filtering
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from typing import List, Dict, Any
import json
import logging
import traceback
from datetime import datetime
import os
from ai_agent import TravelShoppingAgent

# Import the API services
from product_service import ProductService

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatbotOrchestrator:
    """Main orchestrator class - FIXED with proper seasonal handling"""
    
    def __init__(self):
        # Initialize API services
        catalog_url = os.getenv('PRODUCT_CATALOG_URL', 'http://localhost:8080')
        use_grpc = os.getenv('PRODUCT_CATALOG_USE_GRPC', 'false').lower() == 'true'
        self.product_service = ProductService(catalog_service_url=catalog_url, use_grpc=use_grpc)
        
        # Initialize AI agent with error handling
        try:
            self.ai_agent = TravelShoppingAgent()
            self.ai_available = True
        except Exception as e:
            logger.error(f"Failed to initialize AI agent: {e}")
            self.ai_agent = None
            self.ai_available = False
        
        self.request_count = 0
        logger.info("ChatbotOrchestrator initialized with seasonal filtering capabilities")
        
    def process_query(self, user_query: str) -> dict:
        """
        Main processing pipeline - FIXED with proper seasonal filtering
        """
        self.request_count += 1
        request_id = f"req_{self.request_count}_{datetime.now().strftime('%H%M%S')}"
        
        logger.info(f"[{request_id}] Processing query: {user_query}")
        
        try:
            # Step 1: Parse intent with enhanced seasonal detection
            logger.info(f"[{request_id}] Step 1: Parsing intent with seasonal context...")
            intent_data = self._parse_intent(user_query)
            
            # Step 2: Fetch contextual data with seasonal information
            logger.info(f"[{request_id}] Step 2: Fetching contextual data...")
            context_data = self._fetch_context(intent_data)
            
            # Step 3: Get seasonally appropriate products - THIS IS THE KEY FIX
            logger.info(f"[{request_id}] Step 3: Fetching seasonally appropriate products...")
            products = self._get_seasonal_products(intent_data, context_data)
            
            # Step 4: Generate final response with seasonal context
            logger.info(f"[{request_id}] Step 4: Generating seasonal response...")
            response = self._generate_response(user_query, intent_data, context_data, products)
            
            logger.info(f"[{request_id}] Successfully processed query with seasonal context")
            return response
            
        except Exception as e:
            logger.error(f"[{request_id}] Error processing query: {str(e)}")
            logger.error(traceback.format_exc())
            return self._create_error_response(str(e))
    
    def _parse_intent(self, query: str) -> dict:
        """Parse user intent with enhanced seasonal detection"""
        if self.ai_available and self.ai_agent:
            try:
                return self.ai_agent.parse_intent(query)
            except Exception as e:
                logger.error(f"AI intent parsing failed: {e}")
        
        # Fallback intent parsing with seasonal detection
        return self._fallback_intent_parsing(query)
    
    def _fallback_intent_parsing(self, query: str) -> dict:
        """Enhanced fallback with proper seasonal detection"""
        query_lower = query.lower()
        
        # Extract destination
        destination = "unspecified"
        country = None
        city = None
        
        # Country detection
        countries = {
            'pakistan': 'Pakistan',
            'turkey': 'Turkey', 
            'japan': 'Japan',
            'india': 'India',
            'dubai': 'UAE',
            'uae': 'UAE'
        }
        
        for key, value in countries.items():
            if key in query_lower:
                country = value
                destination = value
                break
        
        # Enhanced seasonal detection - THIS IS CRITICAL
        season = "unspecified"
        climate_keywords = []
        weather_concern = False
        
        # Direct season mentions
        if any(word in query_lower for word in ['winter', 'winters']):
            season = 'winter'
            climate_keywords = ['winter', 'cold']
            weather_concern = True
        elif any(word in query_lower for word in ['summer']):
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
        
        # Temperature/weather keywords
        elif 'cold' in query_lower:
            season = 'winter'
            climate_keywords = ['winter', 'cold']
            weather_concern = True
        elif any(word in query_lower for word in ['hot', 'warm']):
            season = 'summer'
            climate_keywords = ['summer', 'hot']
            weather_concern = True
        
        # Month detection
        months = {
            'january': 'winter', 'february': 'winter', 'march': 'spring',
            'april': 'spring', 'may': 'spring', 'june': 'summer',
            'july': 'summer', 'august': 'summer', 'september': 'autumn',
            'october': 'autumn', 'november': 'autumn', 'december': 'winter'
        }
        
        dates = "unspecified"
        for month_name, month_season in months.items():
            if month_name in query_lower:
                dates = month_name.capitalize()
                if season == "unspecified":
                    season = month_season
                    climate_keywords = [month_season, 'seasonal']
                weather_concern = True
                break
        
        # Category detection
        category = "clothing"
        if any(word in query_lower for word in ['gift', 'present', 'souvenir']):
            category = "gifts"
        elif any(word in query_lower for word in ['accessory', 'accessories']):
            category = "accessories"
        elif any(word in query_lower for word in ['pack', 'packing']):
            category = "clothing"  # Packing queries are usually about clothing
        
        return {
            "destination": destination,
            "city": city,
            "country": country,
            "season": season,
            "dates": dates,
            "category": category,
            "climate_keywords": climate_keywords,
            "weather_concern": weather_concern,
            "travel_purpose": "vacation",
            "urgency": "flexible",
            "confidence": 0.8 if season != "unspecified" else 0.6,
            "parsed_with_seasonal_context": season != "unspecified"
        }
    
    def _fetch_context(self, intent_data: dict) -> dict:
        """Fetch cultural context with seasonal climate data"""
        context = {}
        destination = intent_data.get("destination")
        season = intent_data.get("season")
        dates = intent_data.get("dates")
        city = intent_data.get("city")
        cultural_event = intent_data.get("cultural_event")

        if destination and destination != "unspecified":
            try:
                context["destination_info"] = {
                    "name": destination,
                    "season": season,
                    "seasonal_context_available": season != "unspecified"
                }
                logger.info(f"Context prepared for {destination} in {season}")
            except Exception as e:
                logger.error(f"Error fetching context for {destination}: {e}")
                context["destination_info"] = {
                    "name": destination,
                    "error": "Context fetch failed"
                }
            
            # Get seasonal cultural context if AI is available
            if self.ai_available and self.ai_agent:
                try:
                    cultural_context = self.ai_agent.get_cultural_context(
                        destination, season, dates, cultural_event, city
                    )
                    context["cultural"] = cultural_context
                    
                    # Get seasonal climate data specifically
                    if season and season != "unspecified":
                        from cultural_data import CulturalDataManager
                        cultural_manager = CulturalDataManager()
                        
                        # Try to get regional climate data
                        if city:
                            seasonal_climate = cultural_manager.get_regional_climate_data(
                                destination, city, season
                            )
                            if seasonal_climate:
                                context["seasonal_climate"] = seasonal_climate
                                logger.info(f"Added seasonal climate data for {city} in {season}")
                        
                        # Get festival recommendations if relevant
                        festivals = cultural_manager.get_festival_recommendations(
                            destination, dates or season
                        )
                        if festivals:
                            context["relevant_festivals"] = festivals
                            
                except Exception as e:
                    logger.error(f"Cultural context fetch failed: {e}")
            else:
                # Fallback cultural context with seasonal notes
                context["cultural"] = {
                    "destination": destination,
                    "season": season,
                    "cultural_notes": f"Popular destination with rich cultural heritage",
                    "seasonal_notes": f"Consider {season} weather conditions" if season != "unspecified" else "",
                    "local_customs": [],
                    "shopping_recommendations": []
                }
        
        return context
    
    def _get_seasonal_products(self, intent_data: dict, context_data: dict) -> list:
        """
        THE KEY FIX: Get products filtered by season and climate
        """
        try:
            category = intent_data.get("category", "clothing")
            season = intent_data.get("season", "unspecified")
            climate_keywords = intent_data.get("climate_keywords", [])
            destination = intent_data.get("destination")
            city = intent_data.get("city")
            country = intent_data.get("country")
            
            logger.info(f"Getting seasonal products for {destination} in {season} - Category: {category}")
            
            # Step 1: Determine climate filter based on season
            climate_filter = None
            if season == "winter":
                climate_filter = "cold"
            elif season == "summer":
                climate_filter = "hot"
            elif season in ["spring", "autumn"]:
                climate_filter = "mild"
            elif climate_keywords:
                # Use climate keywords to determine filter
                if any(word in climate_keywords for word in ["cold", "winter"]):
                    climate_filter = "cold"
                elif any(word in climate_keywords for word in ["hot", "summer"]):
                    climate_filter = "hot"
                else:
                    climate_filter = "mild"
            
            # Step 2: Determine cultural filter
            cultural_filter = None
            exclude_inappropriate = False
            
            if destination and destination != "unspecified":
                destination_lower = destination.lower()
                if any(place in destination_lower for place in ['pakistan', 'saudi', 'iran']):
                    cultural_filter = 'conservative'
                    exclude_inappropriate = True
                elif any(place in destination_lower for place in ['dubai', 'turkey', 'malaysia']):
                    cultural_filter = 'modest'
                    exclude_inappropriate = True
                elif any(place in destination_lower for place in ['japan', 'korea']):
                    cultural_filter = 'traditional'
            
            # Step 3: Get filtered products using enhanced server capabilities
            logger.info(f"Applying filters - Climate: {climate_filter}, Cultural: {cultural_filter}, Exclude inappropriate: {exclude_inappropriate}")
            
            try:
                filtered_products = self.product_service.get_products_with_filters(
                    category=category,
                    climate=climate_filter,
                    cultural=cultural_filter,
                    exclude_inappropriate=exclude_inappropriate
                )
                
                if filtered_products and len(filtered_products) >= 3:
                    logger.info(f"Server filtering successful: {len(filtered_products)} products")
                    return self._format_products(filtered_products[:6])  # Return top 6
                else:
                    logger.warning(f"Server filtering returned insufficient products: {len(filtered_products) if filtered_products else 0}")
                    
            except Exception as e:
                logger.error(f"Server filtering failed: {e}")
            
            # Step 4: Fallback to manual filtering
            logger.info("Falling back to manual seasonal filtering")
            all_products = self.product_service.get_products(category=category)
            
            # Apply manual seasonal filtering
            seasonally_appropriate = self._filter_products_by_season(all_products, season, climate_keywords)
            
            # Apply cultural filtering
            culturally_filtered = seasonally_appropriate
            if exclude_inappropriate:
                culturally_filtered = [
                    p for p in seasonally_appropriate 
                    if not any('inappropriate' in str(cat).lower() for cat in p.get('categories', []))
                ]
            
            # Apply regional climate filtering if city information is available
            if city and country and len(culturally_filtered) > 10:
                try:
                    climate_filtered = self.product_service.filter_products_by_regional_climate(
                        culturally_filtered, country, city, season
                    )
                    if climate_filtered:
                        culturally_filtered = climate_filtered
                        logger.info(f"Applied regional climate filtering for {city}, {country}")
                except Exception as e:
                    logger.error(f"Regional climate filtering failed: {e}")
            
            final_products = culturally_filtered[:6]  # Limit to 6 products
            logger.info(f"Manual filtering resulted in {len(final_products)} seasonal products")
            
            return self._format_products(final_products)
            
        except Exception as e:
            logger.error(f"Error getting seasonal products: {e}")
            logger.error(traceback.format_exc())
            # Final fallback
            return self._get_fallback_products(intent_data)
    
    def _filter_products_by_season(self, products: List[dict], season: str, climate_keywords: List[str]) -> List[dict]:
        """Filter products based on seasonal appropriateness"""
        if season == "unspecified" and not climate_keywords:
            return products  # No seasonal filtering needed
        
        seasonal_products = []
        
        for product in products:
            name_lower = product.get('name', '').lower()
            description_lower = product.get('description', '').lower()
            categories = [str(cat).lower() for cat in product.get('categories', [])]
            
            is_seasonal_match = False
            
            # Season-specific filtering
            if season == "winter" or any(word in climate_keywords for word in ["winter", "cold"]):
                # Look for winter/cold weather items
                winter_keywords = ['winter', 'warm', 'coat', 'jacket', 'sweater', 'thermal', 'wool', 'fleece', 'parka', 'heavy']
                winter_categories = ['winter', 'cold', 'outerwear', 'warm']
                
                if (any(keyword in name_lower or keyword in description_lower for keyword in winter_keywords) or
                    any(cat in categories for cat in winter_categories)):
                    is_seasonal_match = True
                    
            elif season == "summer" or any(word in climate_keywords for word in ["summer", "hot"]):
                # Look for summer/hot weather items
                summer_keywords = ['summer', 'light', 'cotton', 'linen', 'breathable', 'tank', 'shorts', 't-shirt', 'sun']
                summer_categories = ['summer', 'hot', 'light', 'breathable']
                
                if (any(keyword in name_lower or keyword in description_lower for keyword in summer_keywords) or
                    any(cat in categories for cat in summer_categories)):
                    is_seasonal_match = True
                    
            elif season in ["spring", "autumn"] or any(word in climate_keywords for word in ["mild", "cool"]):
                # Look for transitional weather items
                transitional_keywords = ['light', 'layer', 'jacket', 'cardigan', 'versatile', 'transitional']
                transitional_categories = ['mild', 'layers', 'transitional']
                
                if (any(keyword in name_lower or keyword in description_lower for keyword in transitional_keywords) or
                    any(cat in categories for cat in transitional_categories) or
                    'clothing' in categories):
                    is_seasonal_match = True
            
            # Also include general clothing items that work across seasons
            if not is_seasonal_match:
                general_keywords = ['clothing', 'versatile', 'all-weather', 'universal']
                if (any(keyword in name_lower or keyword in description_lower for keyword in general_keywords) or
                    any(cat in categories for cat in ['clothing', 'accessories', 'unisex'])):
                    is_seasonal_match = True
            
            if is_seasonal_match:
                seasonal_products.append(product)
        
        logger.info(f"Seasonal filtering ({season}) reduced {len(products)} to {len(seasonal_products)} products")
        return seasonal_products
    
    def _format_products(self, products: List[dict]) -> List[dict]:
        """Format products for response with proper price handling"""
        formatted_products = []
        
        for i, product in enumerate(products):
            try:
                formatted_product = {
                    "id": product.get("id", f"PRODUCT_{i}"),
                    "name": product.get("name", "Product"),
                    "price": self._format_price(product.get("priceUsd", product.get("price_usd", {}))),
                    "currency": "USD",
                    "description": product.get("description", "No description available"),
                    "image_url": product.get("picture", "/static/images/default.jpg"),
                    "categories": product.get("categories", []),
                    "cultural_score": product.get("cultural_score", 0.5),
                    "seasonal_relevance": product.get("seasonal_relevance", "General use")
                }
                formatted_products.append(formatted_product)
            except Exception as e:
                logger.error(f"Error formatting product {i}: {e}")
                continue
        
        return formatted_products
    
    def _format_price(self, price_data: dict) -> str:
        """Format price from various price structures"""
        try:
            if not price_data:
                return "$0.00"
            
            # Handle different price formats
            if 'units' in price_data:
                units = price_data.get('units', 0)
                nanos = price_data.get('nanos', 0)
                total_price = units + (nanos / 1_000_000_000)
                return f"{total_price:.2f}"
            elif 'amount' in price_data:
                return f"${price_data['amount']:.2f}"
            else:
                return "$0.00"
        except Exception as e:
            logger.error(f"Error formatting price {price_data}: {e}")
            return "$0.00"
    
    def _get_fallback_products(self, intent_data: dict) -> list:
        """Generate seasonal fallback products"""
        season = intent_data.get("season", "unspecified")
        destination = intent_data.get("destination", "")
        
        if season == "winter":
            return [
                {
                    "id": "WINTER_001",
                    "name": "Heavy Winter Coat",
                    "price": "$199.99",
                    "currency": "USD",
                    "description": "Warm winter coat perfect for cold weather travel",
                    "image_url": "/static/images/winter-coat.jpg",
                    "categories": ["clothing", "outerwear", "winter"],
                    "seasonal_relevance": "Essential for winter travel"
                },
                {
                    "id": "WINTER_002", 
                    "name": "Thermal Underwear Set",
                    "price": "$89.99",
                    "currency": "USD",
                    "description": "Warm base layer for cold climates",
                    "image_url": "/static/images/thermal-set.jpg",
                    "categories": ["clothing", "underwear", "winter"],
                    "seasonal_relevance": "Critical for winter warmth"
                },
                {
                    "id": "WINTER_003",
                    "name": "Wool Scarf",
                    "price": "$45.99",
                    "currency": "USD",
                    "description": "Warm wool scarf for neck protection",
                    "image_url": "/static/images/wool-scarf.jpg",
                    "categories": ["accessories", "winter", "warm"],
                    "seasonal_relevance": "Essential winter accessory"
                }
            ]
        elif season == "summer":
            return [
                {
                    "id": "SUMMER_001",
                    "name": "Light Cotton Shirt",
                    "price": "$49.99",
                    "currency": "USD",
                    "description": "Breathable cotton shirt for hot weather",
                    "image_url": "/static/images/cotton-shirt.jpg",
                    "categories": ["clothing", "shirts", "summer"],
                    "seasonal_relevance": "Perfect for summer heat"
                },
                {
                    "id": "SUMMER_002",
                    "name": "Sun Hat",
                    "price": "$35.99",
                    "currency": "USD",
                    "description": "Wide-brim hat for sun protection",
                    "image_url": "/static/images/sun-hat.jpg",
                    "categories": ["accessories", "summer", "sun-protection"],
                    "seasonal_relevance": "Essential sun protection"
                }
            ]
        else:
            return [
                {
                    "id": "GENERAL_001",
                    "name": "Versatile Travel Jacket",
                    "price": "$129.99",
                    "currency": "USD",
                    "description": "All-season travel jacket suitable for various weather",
                    "image_url": "/static/images/travel-jacket.jpg",
                    "categories": ["clothing", "outerwear", "versatile"],
                    "seasonal_relevance": "Suitable for multiple seasons"
                }
            ]
    
    def _generate_response(self, original_query: str, intent_data: dict, 
                          context_data: dict, products: list) -> dict:
        """Generate final response with seasonal context"""
        if self.ai_available and self.ai_agent:
            try:
                return self.ai_agent.generate_response(
                    original_query, intent_data, context_data, products
                )
            except Exception as e:
                logger.error(f"AI response generation failed: {e}")
        
        # Fallback response generation with seasonal context
        return self._generate_fallback_response(original_query, intent_data, context_data, products)
    
    def _generate_fallback_response(self, query: str, intent_data: dict, 
                                  context_data: dict, products: list) -> dict:
        """Generate a structured fallback response with seasonal context"""
        destination = intent_data.get("destination", "your destination")
        season = intent_data.get("season", "unspecified")
        climate_keywords = intent_data.get("climate_keywords", [])
        
        # Create seasonal narrative
        if season != "unspecified":
            seasonal_context = f"For {season} travel to {destination}, it's important to pack appropriately for the weather conditions."
            narrative = f"Planning for {season} in {destination}? Great choice! "
        elif climate_keywords:
            seasonal_context = f"Given the {', '.join(climate_keywords)} conditions expected in {destination}, proper clothing selection is crucial."
            narrative = f"Considering the weather conditions in {destination}, "
        else:
            seasonal_context = f"When traveling to {destination}, it's wise to prepare for varying weather conditions."
            narrative = f"For your trip to {destination}, "
        
        narrative += f"I've selected {len(products)} items that are both culturally appropriate and suitable for the local climate:"
        
        # Add product descriptions
        for i, product in enumerate(products[:3], 1):
            narrative += f"\n{i}. {product['name']} - {product['description']}"
        
        return {
            "message": narrative,
            "seasonal_context": seasonal_context,
            "products": products,
            "context": {
                "destination": destination,
                "season": season,
                "climate_considerations": climate_keywords,
                "cultural_notes": context_data.get("cultural", {}).get("cultural_notes", "")
            },
            "metadata": {
                "products_count": len(products),
                "ai_powered": False,
                "seasonal_filtering_applied": season != "unspecified",
                "climate_keywords_used": climate_keywords,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _create_error_response(self, error_message: str) -> dict:
        """Create standardized error response"""
        return {
            "error": True,
            "message": "I apologize, but I'm having trouble processing your request right now. Please try again.",
            "error_detail": error_message if app.debug else "Internal error occurred",
            "timestamp": datetime.now().isoformat()
        }

# Initialize orchestrator
orchestrator = ChatbotOrchestrator()

# Flask routes remain the same...
@app.route('/')
def home():
    """Serve the main frontend"""
    try:
        return send_from_directory('frontend', 'index.html')
    except:
        return jsonify({
            "service": "Travel & Culture-Aware Shopping Chatbot - FIXED VERSION",
            "version": "1.1.0",
            "status": "Backend running with seasonal filtering",
            "new_features": ["Proper winter/summer product filtering", "Enhanced seasonal context parsing"],
            "endpoints": {
                "/chat": "POST - Main chat endpoint with seasonal context",
                "/health": "GET - Health check",
                "/test/seasonal": "GET - Test seasonal filtering"
            }
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "requests_processed": orchestrator.request_count,
        "seasonal_filtering": "enabled",
        "services": {
            "cultural_data": "available",
            "products": "available",
            "seasonal_context": "available"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint with seasonal context handling
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({"error": "Query field is required and cannot be empty"}), 400
        
        logger.info(f"Received chat request: {user_query[:100]}...")
        
        # Process query with seasonal context
        response = orchestrator.process_query(user_query)
        
        return jsonify(response), 200 if not response.get('error') else 500
        
    except Exception as e:
        logger.error(f"Unexpected error in /chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal server error occurred",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/test/seasonal')
def test_seasonal():
    """Test seasonal filtering functionality"""
    test_queries = [
        "What should I pack for Pakistan in winters?",
        "Summer clothes for Turkey",
        "What to wear in Japan during spring?",
        "Cold weather gear for mountain travel"
    ]
    
    results = {}
    for query in test_queries:
        try:
            result = orchestrator.process_query(query)
            results[query] = {
                "season_detected": result.get('metadata', {}).get('intent', {}).get('season'),
                "products_count": result.get('metadata', {}).get('products_count', 0),
                "seasonal_filtering_applied": result.get('metadata', {}).get('seasonal_filtering_applied', False)
            }
        except Exception as e:
            results[query] = {"error": str(e)}
    
    return jsonify({
        "seasonal_filtering_test": results,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Travel Chatbot Backend with SEASONAL FILTERING on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info("NEW FEATURES: Proper winter/summer product recommendations!")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
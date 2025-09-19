"""
Travel & Culture-Aware Shopping Chatbot Backend
Flask service that orchestrates AI agent and API calls for GKE Turns 10 Hackathon
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
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
    """Main orchestrator class that coordinates AI agent and API calls"""
    
    def __init__(self):
        # Initialize API services (Member B's code)
        # Initialize ProductService with required catalog endpoint
        catalog_url = os.getenv('PRODUCT_CATALOG_URL', 'http://localhost:8080')
        use_grpc = os.getenv('PRODUCT_CATALOG_USE_GRPC', 'false').lower() == 'true'
        self.product_service = ProductService(catalog_service_url=catalog_url, use_grpc=use_grpc)
        
        # Initialize AI agent (Member A's code) with error handling
        try:
            self.ai_agent = TravelShoppingAgent()
            self.ai_available = True
        except Exception as e:
            logger.error(f"Failed to initialize AI agent: {e}")
            self.ai_agent = None
            self.ai_available = False
        
        self.request_count = 0
        logger.info("ChatbotOrchestrator initialized with AI agent and API services")
        
    def process_query(self, user_query: str) -> dict:
        """
        Main processing pipeline that orchestrates the full workflow
        Args:
            user_query: User's natural language query
        Returns:
            dict: Formatted response with recommendations
        """
        self.request_count += 1
        request_id = f"req_{self.request_count}_{datetime.now().strftime('%H%M%S')}"
        
        logger.info(f"[{request_id}] Processing query: {user_query}")
        
        try:
            # Step 1: Parse intent using AI agent or fallback
            logger.info(f"[{request_id}] Step 1: Parsing intent...")
            intent_data = self._parse_intent(user_query)
            
            # Step 2: Fetch contextual data
            logger.info(f"[{request_id}] Step 2: Fetching contextual data...")
            context_data = self._fetch_context(intent_data)
            
            # Step 3: Get product recommendations
            logger.info(f"[{request_id}] Step 3: Fetching product recommendations...")
            products = self._get_products(intent_data, context_data)
            
            # Step 4: Generate final response
            logger.info(f"[{request_id}] Step 4: Generating final response...")
            response = self._generate_response(user_query, intent_data, context_data, products)
            
            logger.info(f"[{request_id}] Successfully processed query")
            return response
            
        except Exception as e:
            logger.error(f"[{request_id}] Error processing query: {str(e)}")
            logger.error(traceback.format_exc())
            return self._create_error_response(str(e))
    
    def _parse_intent(self, query: str) -> dict:
        """Parse user intent using AI agent with fallback"""
        if self.ai_available and self.ai_agent:
            try:
                return self.ai_agent.parse_intent(query)
            except Exception as e:
                logger.error(f"AI intent parsing failed: {e}")
        
        # Fallback intent parsing using simple keyword detection
        return self._fallback_intent_parsing(query)
    
    def _fallback_intent_parsing(self, query: str) -> dict:
        """Simple keyword-based intent parsing fallback"""
        query_lower = query.lower()
        
        # Extract destination
        destinations = ['japan', 'tokyo', 'dubai', 'turkey', 'istanbul', 'paris', 'london', 'new york']
        destination = "unspecified"
        for dest in destinations:
            if dest in query_lower:
                destination = dest.title()
                break
        
        # Extract season/weather context
        seasons = {
            'winter': ['winter', 'cold', 'snow', 'december', 'january', 'february'],
            'summer': ['summer', 'hot', 'warm', 'june', 'july', 'august'],
            'spring': ['spring', 'march', 'april', 'may'],
            'fall': ['fall', 'autumn', 'september', 'october', 'november']
        }
        
        season = None
        for season_name, keywords in seasons.items():
            if any(keyword in query_lower for keyword in keywords):
                season = season_name
                break
        
        # Extract category
        category = "clothing"  # default
        if any(word in query_lower for word in ['gift', 'present', 'eid']):
            category = "gifts"
        elif any(word in query_lower for word in ['clothes', 'clothing', 'wear', 'pack']):
            category = "clothing"
        
        return {
            "destination": destination,
            "category": category,
            "season": season,
            "dates": None,
            "cultural_event": "eid" if "eid" in query_lower else None,
            "intent_confidence": 0.7
        }
    
    def _fetch_context(self, intent_data: dict) -> dict:
        """Fetch cultural context with integrated climate data"""
        context = {}
        destination = intent_data.get("destination")
        dates = intent_data.get("dates")
        cultural_event = intent_data.get("cultural_event")

        if destination and destination != "unspecified":
            try:
                # Get cultural and climate data from enhanced system
                # This now includes integrated climate data from Wikipedia/weather APIs
                context["destination_info"] = {
                    "name": destination,
                    "climate_integrated": True  # Handled by cultural_data.py
                }
                logger.info(f"Context prepared for {destination}")
            except Exception as e:
                logger.error(f"Error fetching context for {destination}: {e}")
                context["destination_info"] = {
                    "name": destination,
                    "error": "Context fetch failed"
                }
            
            # Get cultural context if AI is available
            if self.ai_available and self.ai_agent:
                try:
                    cultural_context = self.ai_agent.get_cultural_context(
                        destination, dates, cultural_event
                    )
                    context["cultural"] = cultural_context
                    
                    # Get festival recommendations if relevant
                    if dates:
                        festivals = self.ai_agent.cultural_manager.get_festival_recommendations(
                            destination, dates
                        )
                        context["relevant_festivals"] = festivals
                except Exception as e:
                    logger.error(f"Cultural context fetch failed: {e}")
            else:
                # Fallback cultural context
                context["cultural"] = {
                    "destination": destination,
                    "cultural_notes": f"Popular destination with rich cultural heritage",
                    "local_customs": [],
                    "shopping_recommendations": []
                }
        
        return context
    
    def _get_products(self, intent_data: dict, context_data: dict) -> list:
        """Fetch relevant products with improved filtering and error handling"""
        try:
            # Get base category
            category = intent_data.get("category", "clothing")
            
            # Get all products from catalog with explicit error handling
            logger.info(f"Fetching products for category: {category}")
            try:
                all_products = self.product_service.get_products(category=category)
                logger.info(f"Retrieved {len(all_products)} total products")
                
                # Ensure we have products
                if not all_products:
                    logger.warning("No products returned, using direct mock data")
                    all_products = self.product_service._get_mock_products(category=category)
                    
            except Exception as e:
                logger.error(f"Product service failed: {e}")
                # Direct fallback to mock products
                all_products = self.product_service._get_mock_products(category=category)
                logger.info(f"Using {len(all_products)} mock products as fallback")
            
            # Apply cultural relevance filtering (enhanced with seasonal Wikipedia data)
            culturally_relevant = all_products
            destination = intent_data.get("destination")
            if destination and destination != "unspecified":
                cultural_context = context_data.get("cultural", {})
                culturally_relevant = self.product_service.get_culturally_relevant_products(
                    category=category, 
                    cultural_context=cultural_context,
                    destination=destination,
                    month=intent_data.get("dates")
                )
                logger.info(f"Cultural relevance filtering resulted in {len(culturally_relevant)} products")
            
            # Apply MCP cultural filtering if AI is available
            culturally_filtered = culturally_relevant
            if self.ai_available and self.ai_agent:
                try:
                    if destination and destination != "unspecified":
                        culturally_filtered = self.ai_agent.cultural_manager.filter_product_recommendations(
                            culturally_relevant, destination, cultural_context, intent_data.get("dates")
                        )
                        logger.info(f"MCP cultural filtering resulted in {len(culturally_filtered)} products")
                except Exception as e:
                    logger.error(f"MCP cultural filtering failed: {e}")
            
            # Apply regional climate filtering if city information is available
            climate_filtered = culturally_filtered
            city = intent_data.get("city")
            country = intent_data.get("country") or destination
            month = intent_data.get("dates")
            
            if city and country and city != "unspecified":
                try:
                    climate_filtered = self.product_service.filter_products_by_regional_climate(
                        culturally_filtered, country, city, month
                    )
                    logger.info(f"Regional climate filtering resulted in {len(climate_filtered)} products")
                except Exception as e:
                    logger.error(f"Regional climate filtering failed: {e}")
                    climate_filtered = culturally_filtered  # Fallback to previous results
            
            # Format products for response - limit to 6 products
            final_products = climate_filtered[:6]
            formatted_products = []
            
            for i, product in enumerate(final_products):
                try:
                    formatted_product = {
                        "id": product.get("id", f"PRODUCT_{i}"),
                        "name": product.get("name", "Product"),
                        "price": self._format_price(product.get("priceUsd", {})),
                        "currency": "USD",
                        "description": product.get("description", "No description available"),
                        "image_url": product.get("picture", "/static/images/default.jpg"),
                        "categories": product.get("categories", []),
                        "cultural_score": product.get("cultural_score", 0.5)
                    }
                    formatted_products.append(formatted_product)
                except Exception as e:
                    logger.error(f"Error formatting product {i}: {e}")
                    continue
            
            logger.info(f"Returning {len(formatted_products)} formatted products")
            return formatted_products
            
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            logger.error(traceback.format_exc())
            # Return diverse mock products as fallback
            return self._get_fallback_products(intent_data)
    
    def _format_price(self, price_usd: dict) -> str:
        """Format price from the product catalog structure"""
        try:
            if not price_usd:
                return "$0.00"
            
            units = price_usd.get("units", 0)
            nanos = price_usd.get("nanos", 0)
            
            # Convert nanos to decimal (nanos is in billionths)
            decimal_part = nanos / 1_000_000_000
            total_price = units + decimal_part
            
            return f"${total_price:.2f}"
        except Exception as e:
            logger.error(f"Error formatting price {price_usd}: {e}")
            return "$0.00"
    
    def _get_fallback_products(self, intent_data: dict) -> list:
        """Generate diverse fallback products based on intent"""
        category = intent_data.get("category", "clothing")
        destination = intent_data.get("destination", "")
        
        if category == "gifts" or "gift" in intent_data.get("cultural_event", "").lower():
            return [
                {
                    "id": "GIFT001",
                    "name": "Traditional Gift Set",
                    "price": "$39.99",
                    "currency": "USD",
                    "description": "Beautiful traditional gift perfect for cultural occasions",
                    "image_url": "/static/images/gift-set.jpg",
                    "categories": ["gifts", "traditional"],
                    "cultural_score": 0.9
                },
                {
                    "id": "GIFT002", 
                    "name": "Luxury Scarf",
                    "price": "$59.99",
                    "currency": "USD",
                    "description": "Elegant scarf suitable for any occasion",
                    "image_url": "/static/images/scarf.jpg",
                    "categories": ["accessories", "gifts"],
                    "cultural_score": 0.8
                }
            ]
        else:
            return [
                {
                    "id": "CLOTHING001",
                    "name": "Versatile Jacket",
                    "price": "$89.99",
                    "currency": "USD", 
                    "description": "Perfect for varying weather conditions",
                    "image_url": "/static/images/jacket.jpg",
                    "categories": ["clothing", "outerwear"],
                    "cultural_score": 0.7
                },
                {
                    "id": "CLOTHING002",
                    "name": "Comfortable Walking Shoes",
                    "price": "$79.99",
                    "currency": "USD",
                    "description": "Ideal for exploring new destinations",
                    "image_url": "/static/images/shoes.jpg", 
                    "categories": ["footwear", "travel"],
                    "cultural_score": 0.6
                }
            ]
    
    def _generate_response(self, original_query: str, intent_data: dict, 
                          context_data: dict, products: list) -> dict:
        """Generate final response with or without AI"""
        if self.ai_available and self.ai_agent:
            try:
                return self.ai_agent.generate_response(
                    original_query, intent_data, context_data, products
                )
            except Exception as e:
                logger.error(f"AI response generation failed: {e}")
        
        # Fallback response generation
        return self._generate_fallback_response(original_query, intent_data, context_data, products)
    
    def _generate_fallback_response(self, query: str, intent_data: dict, 
                                  context_data: dict, products: list) -> dict:
        """Generate a structured fallback response"""
        destination = intent_data.get("destination", "your destination")
        weather_info = context_data.get("weather", {})
        
        # Create narrative
        narrative = f"Based on your query about {destination}, "
        
        if weather_info.get("summary"):
            narrative += f"I see the weather is {weather_info['summary']}. "
        
        narrative += f"Here are {len(products)} recommended items that would be perfect for your trip:"
        
        # Add product descriptions
        for i, product in enumerate(products[:3], 1):
            narrative += f"\n{i}. {product['name']} - {product['description']}"
        
        return {
            "narrative": narrative,
            "products": products,
            "context": {
                "destination": destination,
                "weather": weather_info.get("summary", "Weather data unavailable"),
                "cultural_notes": context_data.get("cultural", {}).get("cultural_notes", "")
            },
            "metadata": {
                "products_count": len(products),
                "ai_powered": False,
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

@app.route('/')
def home():
    """Serve the main frontend"""
    try:
        return send_from_directory('frontend', 'index.html')
    except:
        # Fallback if frontend folder doesn't exist
        return jsonify({
            "service": "Travel & Culture-Aware Shopping Chatbot",
            "version": "1.0.0",
            "status": "Backend running - Frontend not found in /frontend/",
            "endpoints": {
                "/chat": "POST - Main chat endpoint",
                "/health": "GET - Health check",
                "/docs": "GET - API documentation",
                "/test/weather/<city>": "GET - Test weather API",
                "/test/products": "GET - Test products API"
            }
        })

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "requests_processed": orchestrator.request_count,
        "services": {
            "cultural_data": "available",
            "products": "available",
            "wikipedia_api": "available"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint that handles user queries
    Expected input: {"query": "user's question"}
    Returns: JSON response with recommendations
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({"error": "Query field is required and cannot be empty"}), 400
        
        # Log incoming request
        logger.info(f"Received chat request: {user_query[:100]}...")
        
        # Process query through orchestrator
        response = orchestrator.process_query(user_query)
        
        # Return response
        return jsonify(response), 200 if not response.get('error') else 500
        
    except Exception as e:
        logger.error(f"Unexpected error in /chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal server error occurred",
            "timestamp": datetime.now().isoformat()
        }), 500

# Test endpoints for debugging
@app.route('/test/weather/<city>')
def test_weather(city):
    """Test endpoint for weather functionality - now using integrated climate system"""
    try:
        # Note: Weather functionality is now integrated into cultural_data.py
        # This endpoint is maintained for backward compatibility
        return jsonify({
            "city": city,
            "status": "success",
            "message": "Weather functionality now integrated into cultural recommendations",
            "note": "Use /chat endpoint with travel queries for climate-aware recommendations"
        }), 200
    except Exception as e:
        logger.error(f"Weather test error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test/products')
def test_products():
    """Test endpoint for product catalog API"""
    try:
        category = request.args.get('category')
        products = orchestrator.product_service.get_products(category=category)
        formatted = []
        for p in products[:5]:  # Show first 5
            formatted.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "price": orchestrator.product_service.format_price(p.get("price_usd", {})),
                "categories": p.get("categories", [])
            })
        return jsonify({
            'products': formatted, 
            'total_count': len(products),
            'category_filter': category
        }), 200
    except Exception as e:
        logger.error(f"Products test error: {e}")
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    # Configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Travel Chatbot Backend on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=debug)
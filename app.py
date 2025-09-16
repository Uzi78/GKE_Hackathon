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
from weather_service import WeatherService
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
        self.weather_service = WeatherService()
        self.product_service = ProductService()
        
        # Initialize AI agent (Member A's code)
        self.ai_agent = TravelShoppingAgent()
        
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
            # Step 1: Parse intent using AI agent (Member A's code)
            logger.info(f"[{request_id}] Step 1: Parsing intent...")
            intent_data = self._parse_intent(user_query)
            
            # Step 2: Fetch contextual data (Member B's APIs)
            logger.info(f"[{request_id}] Step 2: Fetching contextual data...")
            context_data = self._fetch_context(intent_data)
            
            # Step 3: Get product recommendations (Member B's catalog API)
            logger.info(f"[{request_id}] Step 3: Fetching product recommendations...")
            products = self._get_products(intent_data, context_data)
            
            # Step 4: Generate final response (Member A's AI agent)
            logger.info(f"[{request_id}] Step 4: Generating final response...")
            response = self._generate_response(user_query, intent_data, context_data, products)
            
            logger.info(f"[{request_id}] Successfully processed query")
            return response
            
        except Exception as e:
            logger.error(f"[{request_id}] Error processing query: {str(e)}")
            logger.error(traceback.format_exc())
            return self._create_error_response(str(e))
    
    def _parse_intent(self, query: str) -> dict:
        """Parse user intent using AI agent (Member A's implementation)"""
        return self.ai_agent.parse_intent(query)
    
    def _fetch_context(self, intent_data: dict) -> dict:
        """Fetch weather and cultural context using real APIs and AI"""
        context = {}
        destination = intent_data.get("destination")
        dates = intent_data.get("dates")
        cultural_event = intent_data.get("cultural_event")
        
        if destination and destination != "unspecified":
            # Get real weather data using Member B's weather service
            weather_data = self.weather_service.get_weather_forecast(destination)
            if weather_data:
                context["weather"] = {
                    "city": weather_data["city"],
                    "country": weather_data["country"], 
                    "summary": self.weather_service.get_weather_summary(destination),
                    "details": weather_data["forecasts"][0] if weather_data["forecasts"] else None,
                    "full_forecast": weather_data["forecasts"][:3]  # 3-day forecast
                }
            
            # Get AI-powered cultural context using Member A's agent
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
        
        return context
    
    def _get_products(self, intent_data: dict, context_data: dict) -> list:
        """Fetch relevant products from catalog using Member B's service with AI filtering"""
        try:
            # Get products based on category
            category = intent_data.get("category", "clothing")
            all_products = self.product_service.get_products(category=category)
            
            # Apply AI-powered cultural filtering using Member A's agent
            destination = intent_data.get("destination")
            if destination and destination != "unspecified":
                cultural_context = context_data.get("cultural", {})
                culturally_filtered = self.ai_agent.cultural_manager.filter_product_recommendations(
                    all_products, destination, cultural_context
                )
            else:
                culturally_filtered = all_products
            
            # Filter products based on weather if available
            weather_data = context_data.get("weather", {}).get("details")
            if weather_data:
                # Create weather data structure for filtering
                weather_for_filtering = {
                    "forecasts": [weather_data]
                }
                weather_filtered = self.product_service.filter_products_by_weather(
                    culturally_filtered, weather_for_filtering
                )
            else:
                weather_filtered = culturally_filtered
            
            # Format products for response
            formatted_products = []
            for product in weather_filtered[:4]:  # Limit to 4 products
                formatted_product = {
                    "id": product.get("id", "N/A"),
                    "name": product.get("name", "Product"),
                    "price": self.product_service.format_price(product.get("price_usd", {})),
                    "currency": "USD",
                    "description": product.get("description", "No description available"),
                    "image_url": product.get("picture", "/static/images/default.jpg"),
                    "categories": product.get("categories", []),
                    "cultural_score": product.get("cultural_score", 0.5)
                }
                formatted_products.append(formatted_product)
            
            return formatted_products
            
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            # Return mock products as fallback
            return [
                {
                    "id": "MOCK001",
                    "name": "Travel Essentials Kit",
                    "price": "$29.99",
                    "currency": "USD",
                    "description": "Perfect for your travel needs",
                    "image_url": "/static/images/travel-kit.jpg",
                    "categories": ["travel"],
                    "cultural_score": 0.8
                }
            ]
    
    def _generate_response(self, original_query: str, intent_data: dict, 
                          context_data: dict, products: list) -> dict:
        """Generate final narrative response using AI agent"""
        return self.ai_agent.generate_response(
            original_query, intent_data, context_data, products
        )
    
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
        return send_from_directory('static', 'index.html')
    except:
        # Fallback if static folder doesn't exist
        return jsonify({
            "service": "Travel & Culture-Aware Shopping Chatbot",
            "version": "1.0.0",
            "status": "Backend running - Frontend not found in /static/",
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
            "weather": "available" if orchestrator.weather_service.api_key else "no_api_key",
            "products": "available"
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
    """Test endpoint for weather API"""
    try:
        weather_data = orchestrator.weather_service.get_weather_forecast(city)
        return jsonify({
            "city": city,
            "weather_data": weather_data,
            "summary": orchestrator.weather_service.get_weather_summary(city)
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
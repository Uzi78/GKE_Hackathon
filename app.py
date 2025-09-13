"""
Travel & Culture-Aware Shopping Chatbot Backend
Flask service that orchestrates AI agent and API calls for GKE Turns 10 Hackathon
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import logging
import traceback
from datetime import datetime
import os

# Import your team members' modules (adjust imports based on actual file structure)
# from ai_agent import TravelShoppingAgent  # Member A's AI agent code
# from api_integrations import WeatherAPI, CatalogAPI  # Member B's API code

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotOrchestrator:
    """Main orchestrator class that coordinates AI agent and API calls"""
    
    def __init__(self):
        # Initialize your team members' components
        # self.ai_agent = TravelShoppingAgent()  # Member A's code
        # self.weather_api = WeatherAPI()        # Member B's code  
        # self.catalog_api = CatalogAPI()        # Member B's code
        self.request_count = 0
        
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
            logger.info(f"[{request_id}] Step 1: Parsing intent with AI agent...")
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
        # TODO: Replace with Member A's actual AI agent call
        # return self.ai_agent.parse_intent(query)
        
        # Mock implementation for testing
        return {
            "destination": "Turkey",
            "dates": "October 2024",
            "category": "clothing",
            "intent": "travel_packing",
            "parsed_successfully": True
        }
    
    def _fetch_context(self, intent_data: dict) -> dict:
        """Fetch weather and cultural context (Member B's implementation)"""
        context = {}
        
        if intent_data.get("destination"):
            # TODO: Replace with Member B's actual API calls
            # context["weather"] = self.weather_api.get_forecast(
            #     destination=intent_data["destination"],
            #     dates=intent_data.get("dates")
            # )
            # context["cultural"] = self.ai_agent.get_cultural_context(
            #     destination=intent_data["destination"],
            #     dates=intent_data.get("dates")
            # )
            
            # Mock implementation
            context = {
                "weather": {
                    "temperature": "18-22°C",
                    "conditions": "mild, occasional rain",
                    "recommendation": "light layers recommended"
                },
                "cultural": {
                    "events": ["Republic Day celebrations"],
                    "norms": "Conservative dress in religious sites",
                    "season": "Autumn tourist season"
                }
            }
        
        return context
    
    def _get_products(self, intent_data: dict, context_data: dict) -> list:
        """Fetch relevant products from catalog (Member B's implementation)"""
        # TODO: Replace with Member B's actual catalog API call
        # return self.catalog_api.search_products(
        #     category=intent_data.get("category"),
        #     filters=self._build_filters(intent_data, context_data)
        # )
        
        # Mock implementation
        return [
            {
                "id": "SKU342",
                "name": "Light Bomber Jacket",
                "price": 49.99,
                "currency": "USD",
                "description": "Perfect for mild autumn weather",
                "image_url": "/static/images/jacket.jpg",
                "category": "outerwear"
            },
            {
                "id": "SKU156", 
                "name": "Waterproof Travel Umbrella",
                "price": 24.99,
                "currency": "USD",
                "description": "Compact umbrella for rainy days",
                "image_url": "/static/images/umbrella.jpg",
                "category": "accessories"
            }
        ]
    
    def _generate_response(self, original_query: str, intent_data: dict, 
                          context_data: dict, products: list) -> dict:
        """Generate final narrative response (Member A's implementation)"""
        # TODO: Replace with Member A's actual AI generation
        # return self.ai_agent.generate_response(
        #     query=original_query,
        #     intent=intent_data,
        #     context=context_data, 
        #     products=products
        # )
        
        # Mock implementation
        explanation = f"""Based on your trip to {intent_data.get('destination', 'your destination')} in {intent_data.get('dates', 'the specified time')}, I recommend these items considering the {context_data.get('weather', {}).get('conditions', 'weather conditions')}. The cultural context suggests {context_data.get('cultural', {}).get('norms', 'being mindful of local customs')}."""
        
        return {
            "message": "Here are my personalized travel recommendations for you!",
            "explanation": explanation,
            "products": products,
            "context": {
                "weather": context_data.get("weather"),
                "cultural": context_data.get("cultural")
            },
            "metadata": {
                "query_processed_at": datetime.now().isoformat(),
                "intent": intent_data
            }
        }
    
    def _create_error_response(self, error_message: str) -> dict:
        """Create standardized error response"""
        return {
            "error": True,
            "message": "I apologize, but I'm having trouble processing your request right now.",
            "error_detail": error_message,
            "timestamp": datetime.now().isoformat()
        }

# Initialize orchestrator
orchestrator = ChatbotOrchestrator()

@app.route('/')
def home():
    """Serve basic info about the service"""
    return jsonify({
        "service": "Travel & Culture-Aware Shopping Chatbot",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Main chat endpoint",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        },
        "status": "running"
    })

@app.route('/health')
def health_check():
    """Health check endpoint for GKE"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "requests_processed": orchestrator.request_count
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

@app.route('/docs')
def docs():
    """API documentation endpoint"""
    docs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Travel Chatbot API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .endpoint { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .method { background: #4CAF50; color: white; padding: 4px 8px; border-radius: 4px; }
            pre { background: #333; color: #fff; padding: 15px; border-radius: 4px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>Travel & Culture-Aware Shopping Chatbot API</h1>
        
        <div class="endpoint">
            <h2><span class="method">POST</span> /chat</h2>
            <p>Main endpoint for processing user travel shopping queries.</p>
            
            <h3>Request Body:</h3>
            <pre>{
  "query": "I'm visiting Turkey in October, what should I pack?"
}</pre>
            
            <h3>Response:</h3>
            <pre>{
  "message": "Here are my personalized travel recommendations for you!",
  "explanation": "Based on your trip to Turkey in October...",
  "products": [
    {
      "id": "SKU342",
      "name": "Light Bomber Jacket", 
      "price": 49.99,
      "currency": "USD",
      "description": "Perfect for mild autumn weather"
    }
  ],
  "context": {
    "weather": {...},
    "cultural": {...}
  }
}</pre>
        </div>
        
        <div class="endpoint">
            <h2><span class="method">GET</span> /health</h2>
            <p>Health check endpoint for monitoring service status.</p>
        </div>
        
        <h2>Example Queries:</h2>
        <ul>
            <li>"I'm visiting Turkey in October, what should I pack?"</li>
            <li>"Show me trending gifts for Eid in Dubai"</li>
            <li>"What clothes should I bring to Japan in winter?"</li>
            <li>"Cultural gifts for Diwali celebration in India"</li>
        </ul>
    </body>
    </html>
    """
    return render_template_string(docs_html)

if __name__ == '__main__':
    # Configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Travel Chatbot Backend on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=debug)
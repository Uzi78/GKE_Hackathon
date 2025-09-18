#!/usr/bin/env python3
"""
Simple Product Catalog Server
Exposes mock products on localhost:8080 for testing
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Mock products data (from your product_service.py)
MOCK_PRODUCTS = [
    {
        'id': 'OLJCESPC7Z',
        'name': 'Sunglasses',
        'description': 'Add a modern touch to your outfits with these sleek aviator sunglasses.',
        'picture': '/static/img/products/sunglasses.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 19, 'nanos': 990000000},
        'categories': ['accessories', 'summer', 'hot']
    },
    {
        'id': '66VCHSJNUP',
        'name': 'Tank Top',
        'description': 'Perfectly cropped cotton tank, with a scooped neckline.',
        'picture': '/static/img/products/tank-top.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 18, 'nanos': 990000000},
        'categories': ['clothing', 'tops', 'summer', 'hot']
    },
    {
        'id': '1YMWWN1N4O',
        'name': 'Watch',
        'description': 'This gold-tone stainless steel watch will work with most of your outfits.',
        'picture': '/static/img/products/watch.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 109, 'nanos': 990000000},
        'categories': ['accessories', 'all-weather']
    },
    {
        'id': 'L9ECAV7KIM',
        'name': 'Loafers',
        'description': 'A neat addition to your summer wardrobe.',
        'picture': '/static/img/products/loafers.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 89, 'nanos': 990000000},
        'categories': ['footwear', 'mild', 'summer']
    },
    {
        'id': '2ZYFJ3GM2N',
        'name': 'Hairdryer',
        'description': "This lightweight hairdryer has 3 heat and speed settings. It's perfect for travel.",
        'picture': '/static/img/products/hairdryer.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 24, 'nanos': 990000000},
        'categories': ['beauty', 'home', 'all-weather']
    },
    {
        'id': '0PUK6V6EV0',
        'name': 'Candle Holder',
        'description': 'This small but intricate candle holder is an excellent gift.',
        'picture': '/static/img/products/candle-holder.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 18, 'nanos': 990000000},
        'categories': ['decor', 'home', 'all-weather']
    },
    {
        'id': 'LS4PSXUNUM',
        'name': 'Salt & Pepper Shakers',
        'description': 'Add some flavor to your kitchen.',
        'picture': '/static/img/products/salt-and-pepper-shakers.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 18, 'nanos': 490000000},
        'categories': ['kitchen', 'all-weather']
    },
    {
        'id': '9SIQT8TOJO',
        'name': 'Bamboo Glass Jar',
        'description': 'This bamboo glass jar can hold 57 oz (1.7 l) and is perfect for any kitchen.',
        'picture': '/static/img/products/bamboo-glass-jar.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 5, 'nanos': 490000000},
        'categories': ['kitchen', 'all-weather']
    },
    {
        'id': '6E92ZMYYFZ',
        'name': 'Mug',
        'description': 'A simple mug with a mustard interior.',
        'picture': '/static/img/products/mug.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 8, 'nanos': 990000000},
        'categories': ['kitchen', 'all-weather']
    },
    {
        'id': 'JKTSNW123',
        'name': 'Winter Jacket',
        'description': 'A heavy-duty insulated jacket to keep you warm during cold winters.',
        'picture': '/static/img/products/winter-jacket.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 149, 'nanos': 990000000},
        'categories': ['clothing', 'outerwear', 'winter', 'cold']
    },
    {
        'id': 'HDY1234',
        'name': 'Hoodie',
        'description': 'A soft cotton hoodie, perfect for layering in cool weather.',
        'picture': '/static/img/products/hoodie.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 49, 'nanos': 990000000},
        'categories': ['clothing', 'tops', 'mild', 'cold']
    },
    {
        'id': 'SWTR567',
        'name': 'Wool Sweater',
        'description': 'Stay cozy with this knitted wool sweater.',
        'picture': '/static/img/products/sweater.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 59, 'nanos': 990000000},
        'categories': ['clothing', 'cold']
    },
    {
        'id': 'RNB123',
        'name': 'Umbrella',
        'description': 'A compact waterproof umbrella for rainy days.',
        'picture': '/static/img/products/umbrella.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 15, 'nanos': 990000000},
        'categories': ['accessories', 'rain', 'all-weather']
    },
    {
        'id': 'TSHRT888',
        'name': 'T-Shirt',
        'description': 'Classic cotton t-shirt, lightweight and breathable.',
        'picture': '/static/img/products/t-shirt.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 20, 'nanos': 990000000},
        'categories': ['clothing', 'summer', 'hot']
    },
    {
        'id': 'SHRTS555',
        'name': 'Shorts',
        'description': 'Casual shorts, perfect for hot days and vacations.',
        'picture': '/static/img/products/shorts.jpg',
        'priceUsd': {'currency_code': 'USD', 'units': 25, 'nanos': 990000000},
        'categories': ['clothing', 'summer', 'hot']
    }
]

# Add price_usd for backward compatibility
for product in MOCK_PRODUCTS:
    if 'price_usd' not in product and 'priceUsd' in product:
        product['price_usd'] = product['priceUsd']

@app.route('/')
def home():
    """Root endpoint with API documentation"""
    return jsonify({
        "service": "Mock Product Catalog API",
        "version": "1.0.0",
        "endpoints": {
            "/": "GET - This documentation",
            "/products": "GET - List all products (supports ?category= filter)",
            "/products/<product_id>": "GET - Get specific product by ID",
            "/categories": "GET - List all available categories",
            "/health": "GET - Health check"
        },
        "total_products": len(MOCK_PRODUCTS)
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "products_available": len(MOCK_PRODUCTS)
    })

@app.route('/products')
def get_products():
    """
    Get all products or filter by category
    Query parameters:
    - category: Filter products by category (case-insensitive)
    - search: Search in product name and description
    - limit: Maximum number of products to return
    """
    products = MOCK_PRODUCTS.copy()
    
    # Filter by category if provided
    category = request.args.get('category', '').strip().lower()
    if category:
        products = [
            p for p in products
            if any(category in cat.lower() for cat in p.get('categories', []))
        ]
    
    # Search filter if provided
    search = request.args.get('search', '').strip().lower()
    if search:
        products = [
            p for p in products
            if (search in p.get('name', '').lower() or 
                search in p.get('description', '').lower())
        ]
    
    # Limit results if provided
    limit = request.args.get('limit')
    if limit:
        try:
            limit = int(limit)
            products = products[:limit]
        except ValueError:
            pass
    
    logger.info(f"Returning {len(products)} products (category: {category or 'all'}, search: {search or 'none'})")
    
    return jsonify(products)

@app.route('/products/<product_id>')
def get_product(product_id):
    """Get a specific product by ID"""
    product = next((p for p in MOCK_PRODUCTS if p['id'] == product_id), None)
    
    if product:
        logger.info(f"Found product: {product_id}")
        return jsonify(product)
    else:
        logger.warning(f"Product not found: {product_id}")
        return jsonify({"error": "Product not found"}), 404

@app.route('/categories')
def get_categories():
    """Get all unique categories"""
    categories = set()
    for product in MOCK_PRODUCTS:
        categories.update(product.get('categories', []))
    
    return jsonify({
        "categories": sorted(list(categories)),
        "count": len(categories)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Starting Mock Product Catalog Server...")
    print("Available at: http://localhost:8080")
    print("API Documentation: http://localhost:8080")
    print("All products: http://localhost:8080/products")
    print("Filter by category: http://localhost:8080/products?category=clothing")
    print("Search products: http://localhost:8080/products?search=jacket")
    print()
    
    app.run(host='0.0.0.0', port=8080, debug=True)
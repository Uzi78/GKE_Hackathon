# product_service.py
import requests
from typing import List, Dict, Optional
import json
import logging

class ProductService:
    def __init__(self, catalog_service_url: str = None):
        self.catalog_service_url = catalog_service_url or "http://productcatalogservice:3550"
        self.logger = logging.getLogger(__name__)
        
    def get_products(self, category: str = None, search_query: str = None) -> List[Dict]:
        """
        Fetch products from Online Boutique catalog or mock data
        """
        try:
            # Try to fetch from actual catalog service first
            return self._get_products_rest(category, search_query)
        except Exception as e:
            self.logger.warning(f"Product catalog service unavailable: {e}")
            return self._get_mock_products(category)
    
    def _get_products_rest(self, category: str = None, search_query: str = None) -> List[Dict]:
        """REST API approach for Online Boutique"""
        try:
            url = f"{self.catalog_service_url}/products"
            self.logger.info(f"Fetching products from: {url}")
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            products = response.json()
            
            # Filter by category if specified
            if category and isinstance(products, list):
                category_lower = category.lower()
                products = [p for p in products 
                           if any(category_lower in cat.lower() 
                                 for cat in p.get('categories', []))]
            
            # Filter by search query if specified
            if search_query and isinstance(products, list):
                search_lower = search_query.lower()
                products = [p for p in products 
                          if search_lower in p.get('name', '').lower() 
                          or search_lower in p.get('description', '').lower()]
            
            self.logger.info(f"Retrieved {len(products)} products from catalog")
            return products
            
        except Exception as e:
            self.logger.error(f"REST API error: {e}")
            raise
    
    def _get_mock_products(self, category: str = None) -> List[Dict]:
        """Fallback mock products that mimic Online Boutique structure"""
        self.logger.info("Using mock product data")
        
        mock_products = [
            {
                'id': 'OLJCESPC7Z',
                'name': 'Sunglasses',
                'description': 'Add a modern touch to your look with these sleek aviator sunglasses.',
                'picture': '/static/img/products/sunglasses.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 19, 'nanos': 990000000},
                'categories': ['accessories']
            },
            {
                'id': '66VCHSJNUP',
                'name': 'Tank Top',
                'description': 'Perfectly cropped cotton tank, with a scooped neckline.',
                'picture': '/static/img/products/tank-top.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 18, 'nanos': 990000000},
                'categories': ['clothing']
            },
            {
                'id': '2ZYFJ3GM2N',
                'name': 'Watch',
                'description': 'This gold-tone stainless steel watch will work with most of your outfits.',
                'picture': '/static/img/products/watch.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 109, 'nanos': 990000000},
                'categories': ['accessories']
            },
            {
                'id': '0PUK6V6EV0',
                'name': 'Vintage Typewriter',
                'description': 'This typewriter looks good in your living room or study.',
                'picture': '/static/img/products/typewriter.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 67, 'nanos': 990000000},
                'categories': ['vintage']
            },
            {
                'id': '1YMWWN1N4O',
                'name': 'Home & Garden Bamboo Cutting Board',
                'description': 'Beautiful, functional, and durable, this bamboo cutting board makes a great gift.',
                'picture': '/static/img/products/bamboo-cutting-board.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 27, 'nanos': 990000000},
                'categories': ['kitchen', 'home']
            },
            {
                'id': 'L9ECAV7KIM',
                'name': 'Loafers',
                'description': 'A neat addition to your summer wardrobe.',
                'picture': '/static/img/products/loafers.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 89, 'nanos': 990000000},
                'categories': ['footwear']
            },
            {
                'id': 'LS4PSXUNUM',
                'name': 'Salt & Pepper Shakers',
                'description': 'Add some flavor to your kitchen.',
                'picture': '/static/img/products/salt-and-pepper-shakers.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 18, 'nanos': 490000000},
                'categories': ['kitchen']
            },
            {
                'id': '9SIQT8TOJO',
                'name': 'City Bike',
                'description': 'This single gear bike probably cannot climb mountains or win a race, but it can get you across the city.',
                'picture': '/static/img/products/city-bike.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 789, 'nanos': 500000000},
                'categories': ['cycling']
            },
            {
                'id': '6E92ZMYYFZ',
                'name': 'Air Plant',
                'description': 'This air plant will give your home a modern and artistic edge.',
                'picture': '/static/img/products/air-plant.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 12, 'nanos': 300000000},
                'categories': ['plant']
            }
        ]
        
        if category:
            category_lower = category.lower()
            filtered = [p for p in mock_products 
                       if any(category_lower in cat.lower() for cat in p['categories'])]
            if filtered:
                return filtered
            
        return mock_products

    def filter_products_by_weather(self, products: List[Dict], weather_data: Dict) -> List[Dict]:
        """Filter products based on weather conditions"""
        if not weather_data or not weather_data.get('forecasts'):
            return products
        
        avg_temp = sum(f['temperature'] for f in weather_data['forecasts']) / len(weather_data['forecasts'])
        weather_main = weather_data['forecasts'][0]['main'].lower()
        
        filtered_products = []
        
        for product in products:
            name_lower = product.get('name', '').lower()
            categories = [cat.lower() for cat in product.get('categories', [])]
            
            # Temperature-based filtering
            if avg_temp < 10:  # Cold weather
                if any(word in name_lower for word in ['jacket', 'coat', 'sweater', 'hoodie', 'warm', 'watch']):
                    filtered_products.append(product)
            elif avg_temp > 25:  # Hot weather
                if any(word in name_lower for word in ['tank', 'shorts', 't-shirt', 'sunglasses', 'hat', 'loafers']):
                    filtered_products.append(product)
            else:  # Mild weather
                if any(word in name_lower for word in ['watch', 'loafers', 'sunglasses']) or 'accessories' in categories:
                    filtered_products.append(product)
            
            # Weather condition-based filtering
            if 'rain' in weather_main and any(word in name_lower for word in ['umbrella', 'jacket', 'waterproof']):
                if product not in filtered_products:
                    filtered_products.append(product)
        
        return filtered_products if filtered_products else products[:3]  # Fallback to first 3 products
    
    def format_price(self, price_usd: Dict) -> str:
        """Format price from Online Boutique format to display string"""
        if not price_usd:
            return "Price unavailable"
        
        units = price_usd.get('units', 0)
        nanos = price_usd.get('nanos', 0)
        total_price = units + (nanos / 1000000000)
        
        return f"${total_price:.2f}"
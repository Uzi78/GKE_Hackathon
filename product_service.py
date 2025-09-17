# product_service.py
import requests
import grpc
from typing import List, Dict, Optional
import json
import logging

class ProductService:
    def __init__(self, catalog_service_url: str, use_grpc: bool = False):
        self.catalog_service_url = catalog_service_url
        self.use_grpc = use_grpc
        
    def get_products(self, category: str = None, search_query: str = None) -> List[Dict]:
        """
        Fetch products from Online Boutique catalog
        """
        try:
            if self.use_grpc:
                return self._get_products_grpc(category, search_query)
            else:
                return self._get_products_rest(category, search_query)
                
        except Exception as e:
            logging.error(f"Product catalog error: {e}")
            return self._get_mock_products(category)
    
    def _get_products_rest(self, category: str = None, search_query: str = None) -> List[Dict]:
        """REST API approach"""
        try:
            url = f"{self.catalog_service_url}/products"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            products = response.json()
            
            # Filter by category if specified
            if category:
                products = [p for p in products if category.lower() in p.get('categories', []).lower()]
            
            # Filter by search query if specified
            if search_query:
                search_lower = search_query.lower()
                products = [p for p in products 
                          if search_lower in p.get('name', '').lower() 
                          or search_lower in p.get('description', '').lower()]
            
            return products
            
        except Exception as e:
            logging.error(f"REST API error: {e}")
            raise
    
    def _get_products_grpc(self, category: str = None, search_query: str = None) -> List[Dict]:
        """gRPC approach (if needed)"""
        # Implementation for gRPC calls to productcatalogservice
        # This would require the proto files from Online Boutique
        try:
            # Example gRPC implementation
            channel = grpc.insecure_channel(self.catalog_service_url)
            # stub = ProductCatalogServiceStub(channel)
            # response = stub.ListProducts(ListProductsRequest())
            # return [self._proto_to_dict(product) for product in response.products]
            
            # For now, fallback to REST
            return self._get_products_rest(category, search_query)
            
        except Exception as e:
            logging.error(f"gRPC error: {e}")
            raise
    
    def _get_mock_products(self, category: str = None) -> List[Dict]:
        """Fallback mock products"""
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
                'id': '1YMWWN1N4O',
                'name': 'Home & Garden Bamboo Cutting Board',
                'description': 'Beautiful, functional, and durable, this bamboo cutting board makes a great gift.',
                'picture': '/static/img/products/bamboo-cutting-board.jpg',
                'price_usd': {'currency_code': 'USD', 'units': 27, 'nanos': 990000000},
                'categories': ['home']
            }
        ]
        
        if category:
            mock_products = [p for p in mock_products if category.lower() in p['categories']]
            
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
                if any(word in name_lower for word in ['jacket', 'coat', 'sweater', 'hoodie', 'warm']):
                    filtered_products.append(product)
            elif avg_temp > 25:  # Hot weather
                if any(word in name_lower for word in ['tank', 'shorts', 't-shirt', 'sunglasses', 'hat']):
                    filtered_products.append(product)
            else:  # Mild weather
                filtered_products.append(product)
            
            # Weather condition-based filtering
            if 'rain' in weather_main and any(word in name_lower for word in ['umbrella', 'jacket', 'waterproof']):
                if product not in filtered_products:
                    filtered_products.append(product)
        
        return filtered_products if filtered_products else products[:5]  # Fallback to first 5 products
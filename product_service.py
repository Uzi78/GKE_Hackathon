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
        self.logger = logging.getLogger(__name__)
        
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
            self.logger.error(f"Product catalog error: {e}")
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
                products = [p for p in products if category.lower() in [cat.lower() for cat in p.get('categories', [])]]
            
            # Filter by search query if specified
            if search_query:
                search_lower = search_query.lower()
                products = [p for p in products 
                          if search_lower in p.get('name', '').lower() 
                          or search_lower in p.get('description', '').lower()]
            
            return products
            
        except Exception as e:
            self.logger.error(f"REST API error: {e}")
            raise
    
    def _get_products_grpc(self, category: str = None, search_query: str = None) -> List[Dict]:
        """gRPC approach (if needed)"""
        try:
            # For now, fallback to REST
            return self._get_products_rest(category, search_query)
            
        except Exception as e:
            self.logger.error(f"gRPC error: {e}")
            raise
    
    def _get_mock_products(self, category: str = None) -> List[Dict]:
        """Fallback mock products"""
        mock_products = [
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
            # Weather-appropriate items
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
                'id': 'HDY9212',
                'name': 'Hoodie_1',
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
        
        # Fixed filtering logic
        if category:
            category_lower = category.lower()
            mock_products = [p for p in mock_products 
                           if any(category_lower in cat.lower() for cat in p.get('categories', []))]
            
        self.logger.info(f"Returning {len(mock_products)} mock products for category: {category}")
        return mock_products

    def filter_products_by_weather(self, products: List[Dict], weather_data: Dict) -> List[Dict]:
        """Filter products based on weather conditions"""
        if not weather_data or not weather_data.get('forecasts'):
            self.logger.warning("No weather data available for filtering")
            return products[:10]  # Return first 10 products as fallback
        
        forecasts = weather_data.get('forecasts', [])
        if not forecasts:
            return products[:10]
            
        avg_temp = sum(f.get('temperature', 20) for f in forecasts) / len(forecasts)
        weather_main = forecasts[0].get('main', '').lower() if forecasts else ''
        
        self.logger.info(f"Filtering products by weather - Avg temp: {avg_temp}°C, Condition: {weather_main}")
        
        filtered_products = []
        all_weather_products = []
        
        for product in products:
            name_lower = product.get('name', '').lower()
            description_lower = product.get('description', '').lower()
            categories = [cat.lower() for cat in product.get('categories', [])]
            
            # Collect all-weather items as backup
            if 'all-weather' in categories:
                all_weather_products.append(product)
            
            # Temperature-based filtering
            temp_match = False
            if avg_temp < 10:  # Cold weather
                cold_keywords = ['jacket', 'coat', 'sweater', 'hoodie', 'warm', 'winter', 'wool']
                cold_categories = ['cold', 'winter', 'outerwear']
                if (any(keyword in name_lower or keyword in description_lower for keyword in cold_keywords) or
                    any(cat in categories for cat in cold_categories)):
                    temp_match = True
                    
            elif avg_temp > 25:  # Hot weather  
                hot_keywords = ['tank', 'shorts', 't-shirt', 'sunglasses', 'hat', 'summer']
                hot_categories = ['hot', 'summer']
                if (any(keyword in name_lower or keyword in description_lower for keyword in hot_keywords) or
                    any(cat in categories for cat in hot_categories)):
                    temp_match = True
                    
            else:  # Mild weather (10-25°C)
                mild_categories = ['mild', 'all-weather']
                # For mild weather, include more general items
                if (any(cat in categories for cat in mild_categories) or 
                    'clothing' in categories):
                    temp_match = True
            
            # Weather condition-based filtering
            condition_match = False
            if 'rain' in weather_main:
                rain_keywords = ['umbrella', 'waterproof', 'rain']
                if any(keyword in name_lower or keyword in description_lower for keyword in rain_keywords):
                    condition_match = True
            
            # Add product if it matches temperature or weather conditions
            if temp_match or condition_match:
                filtered_products.append(product)
        
        # If no specific matches, include all-weather products
        if not filtered_products:
            filtered_products.extend(all_weather_products)
        
        # Final fallback - return some products
        if not filtered_products:
            filtered_products = products[:8]
            
        self.logger.info(f"Weather filtering resulted in {len(filtered_products)} products")
        return filtered_products
    
    def filter_products_by_regional_climate(self, products: List[Dict], country: str, city: str = None, month: str = None) -> List[Dict]:
        """Filter products based on regional climate data from cultural database"""
        try:
            from cultural_data import CulturalDataManager
            cultural_manager = CulturalDataManager()
            
            # Get regional climate data
            regional_data = cultural_manager.get_regional_climate_data(country, city, month)
            
            if regional_data and "current_month_weather" in regional_data:
                month_weather = regional_data["current_month_weather"]
                temp_range = month_weather.get("temp_range", "")
                description = month_weather.get("description", "").lower()
                clothing = month_weather.get("clothing", "").lower()
                
                # Extract average temperature from range (e.g., "15-25°C" -> 20°C)
                avg_temp = self._extract_average_temp(temp_range)
                
                self.logger.info(f"Filtering by regional climate - {city}, {country} in {month}: {temp_range}, {description}")
                
                return self._filter_by_climate_conditions(products, avg_temp, description, clothing)
            
            # Fallback to general country filtering
            elif regional_data:
                self.logger.info(f"Using general regional data for {city}, {country}")
                return self._filter_by_climate_conditions(products, 20, "moderate", "moderate layers")
            
            else:
                self.logger.warning(f"No regional climate data found for {city}, {country}")
                return products[:10]  # Return first 10 as fallback
                
        except Exception as e:
            self.logger.error(f"Error filtering by regional climate: {e}")
            return products[:10]
    
    def _extract_average_temp(self, temp_range: str) -> float:
        """Extract average temperature from a range string like '15-25°C'"""
        try:
            # Remove °C and split by dash
            temp_str = temp_range.replace("°C", "").strip()
            if "-" in temp_str:
                parts = temp_str.split("-")
                min_temp = float(parts[0].strip())
                max_temp = float(parts[1].strip())
                return (min_temp + max_temp) / 2
            else:
                # Single temperature value
                return float(temp_str)
        except (ValueError, IndexError):
            self.logger.warning(f"Could not parse temperature range: {temp_range}")
            return 20.0  # Default moderate temperature
    
    def _filter_by_climate_conditions(self, products: List[Dict], avg_temp: float, description: str, clothing: str) -> List[Dict]:
        """Filter products based on specific climate conditions"""
        filtered_products = []
        all_weather_products = []
        
        for product in products:
            name_lower = product.get('name', '').lower()
            description_lower = product.get('description', '').lower()
            categories = [cat.lower() for cat in product.get('categories', [])]
            
            # Collect all-weather items as backup
            if 'all-weather' in categories:
                all_weather_products.append(product)
            
            # Temperature-based filtering
            temp_match = False
            if avg_temp < 10:  # Cold weather
                cold_keywords = ['jacket', 'coat', 'sweater', 'hoodie', 'warm', 'winter', 'wool', 'thermal']
                cold_categories = ['cold', 'winter', 'outerwear']
                if (any(keyword in name_lower or keyword in description_lower for keyword in cold_keywords) or
                    any(cat in categories for cat in cold_categories)):
                    temp_match = True
                    
            elif avg_temp > 25:  # Hot weather  
                hot_keywords = ['tank', 'shorts', 't-shirt', 'sunglasses', 'hat', 'summer', 'light', 'breathable']
                hot_categories = ['hot', 'summer']
                if (any(keyword in name_lower or keyword in description_lower for keyword in hot_keywords) or
                    any(cat in categories for cat in hot_categories)):
                    temp_match = True
                    
            else:  # Mild weather (10-25°C)
                mild_keywords = ['jacket', 'layers', 'light', 'casual']
                mild_categories = ['mild', 'all-weather', 'clothing']
                if (any(keyword in name_lower or keyword in description_lower for keyword in mild_keywords) or
                    any(cat in categories for cat in mild_categories)):
                    temp_match = True
            
            # Climate description-based filtering
            condition_match = False
            if 'cold' in description or 'freezing' in description:
                if any(keyword in clothing for keyword in ['heavy coat', 'thermal', 'warm layers']):
                    condition_match = True
            elif 'hot' in description or 'warm' in description:
                if any(keyword in clothing for keyword in ['light cotton', 'breathable', 'sun protection']):
                    condition_match = True
            
            # Add product if it matches temperature or climate conditions
            if temp_match or condition_match:
                filtered_products.append(product)
        
        # If no specific matches, include all-weather products
        if not filtered_products:
            filtered_products.extend(all_weather_products[:5])  # Limit to 5 all-weather items
        
        # Final fallback - return some products
        if not filtered_products:
            filtered_products = products[:8]
            
        self.logger.info(f"Regional climate filtering resulted in {len(filtered_products)} products")
        return filtered_products

    def get_products_for_destination(self, destination: str, weather_data: Dict = None, category: str = None) -> List[Dict]:
        """Get products specifically filtered for a destination and weather"""
        try:
            # Get base products
            all_products = self.get_products(category=category)
            
            # Apply weather filtering if weather data is available
            if weather_data:
                filtered_products = self.filter_products_by_weather(all_products, weather_data)
            else:
                filtered_products = all_products
            
            self.logger.info(f"Retrieved {len(filtered_products)} products for destination: {destination}")
            return filtered_products
            
        except Exception as e:
            self.logger.error(f"Error getting products for destination {destination}: {e}")
            return self._get_mock_products()[:5]
    
    def calculate_total_price(self, product_ids: List[str]) -> str:
        """
        Calculate the total price of a list of products by their IDs
        """
        try:
            products = self.get_products()
            total_price = sum(product.get('priceUsd', {}).get('units', 0) for product in products if product.get('id') in product_ids)
            
            return f"${total_price:.2f}"
        except Exception as e:
            self.logger.error(f"Error calculating total price: {e}")
            return "$0.00"
    
    def get_culturally_relevant_products(self, category: str = None, cultural_context: Dict = None, 
                                       destination: str = None, month: str = None) -> List[Dict]:
        """
        Get products that are culturally appropriate for the destination and time
        """
        products = self.get_products(category=category)
        
        if not cultural_context or not destination:
            return products
        
        # Enhanced filtering based on cultural context
        filtered_products = []
        
        for product in products:
            product_name = product.get("name", "").lower()
            product_description = product.get("description", "").lower()
            categories = [cat.lower() for cat in product.get("categories", [])]
            
            # Cultural appropriateness score
            score = self._calculate_cultural_relevance_score(product, cultural_context, destination, month)
            
            if score > 0.3:  # Only include products with decent cultural relevance
                product_copy = product.copy()
                product_copy["cultural_relevance"] = score
                filtered_products.append(product_copy)
        
        # Sort by cultural relevance
        filtered_products.sort(key=lambda x: x.get("cultural_relevance", 0), reverse=True)
        
        return filtered_products[:8]  # Return top 8 culturally relevant products
    
    def _calculate_cultural_relevance_score(self, product: Dict, cultural_context: Dict, 
                                          destination: str, month: str = None) -> float:
        """
        Calculate how culturally relevant a product is for the given context
        Uses seasonal information from Wikipedia instead of weather API
        """
        score = 0.5  # Base score
        
        product_name = product.get("name", "").lower()
        categories = [cat.lower() for cat in product.get("categories", [])]
        
        # Check clothing norms
        clothing_norms = cultural_context.get("clothing_norms", {})
        
        # Religious sites consideration
        if clothing_norms.get("religious_sites"):
            if any(word in product_name for word in ["modest", "long", "cover", "scarf"]):
                score += 0.3
        
        # Business attire
        if clothing_norms.get("business"):
            if any(word in product_name for word in ["formal", "suit", "blazer", "dress"]):
                score += 0.2
        
        # Casual wear
        if clothing_norms.get("casual"):
            if any(word in product_name for word in ["casual", "comfortable", "jeans", "t-shirt"]):
                score += 0.1
        
        # Seasonal weather consideration (from Wikipedia)
        seasonal_weather = cultural_context.get("seasonal_weather", {})
        if month and seasonal_weather:
            # Map month to season
            month_lower = month.lower()
            if month_lower in ['december', 'january', 'february']:
                season = 'winter'
            elif month_lower in ['march', 'april', 'may']:
                season = 'spring'
            elif month_lower in ['june', 'july', 'august']:
                season = 'summer'
            else:  # September, October, November
                season = 'autumn'
            
            season_info = seasonal_weather.get(season, "").lower()
            
            # Adjust score based on seasonal recommendations
            if season == 'winter' and any(word in season_info for word in ['cold', 'snow', 'freezing']):
                if any(word in product_name for word in ['coat', 'jacket', 'warm', 'wool']):
                    score += 0.4
            elif season == 'summer' and any(word in season_info for word in ['hot', 'warm', 'tropical']):
                if any(word in product_name for word in ['short', 'tank', 'light', 'cotton']):
                    score += 0.4
        
        # Festival-specific relevance
        festivals = cultural_context.get("festivals", [])
        for festival in festivals:
            festival_name = festival.get("name", "").lower()
            shopping_relevance = festival.get("shopping_relevance", "").lower()
            
            # Check if product matches festival shopping suggestions
            if any(keyword in shopping_relevance for keyword in ["clothing", "attire", "wear"]):
                if "traditional" in shopping_relevance and "traditional" in product_name:
                    score += 0.4
                elif "festive" in shopping_relevance and any(word in product_name for word in ["colorful", "bright", "party"]):
                    score += 0.3
        
        # Taboo checking (reduce score for inappropriate items)
        taboos = cultural_context.get("taboos", [])
        for taboo in taboos:
            taboo_lower = taboo.lower()
            if (taboo_lower in product_name or 
                any(taboo_lower in cat for cat in categories)):
                score -= 0.5
        
        return max(0.0, min(1.0, score))
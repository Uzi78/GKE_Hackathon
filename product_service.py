# product_service.py - Updated to use Product Server API
import requests
import grpc
from typing import List, Dict, Optional
import json
import logging

class ProductService:
    def __init__(self, catalog_service_url: str, use_grpc: bool = False):
        self.catalog_service_url = catalog_service_url.rstrip('/')  # Remove trailing slash
        self.use_grpc = use_grpc
        self.logger = logging.getLogger(__name__)
        
        # Test connection on initialization
        self._test_connection()
        
    def _test_connection(self):
        """Test connection to product server on initialization"""
        try:
            response = requests.get(f"{self.catalog_service_url}/health", timeout=5)
            if response.status_code == 200:
                self.logger.info(f"Successfully connected to product catalog at {self.catalog_service_url}")
            else:
                self.logger.warning(f"Product catalog responded with status {response.status_code}")
        except Exception as e:
            self.logger.error(f"Failed to connect to product catalog: {e}")
    
    def get_products(self, category: str = None, search_query: str = None) -> List[Dict]:
        """
        Fetch products from Enhanced Product Catalog Server
        """
        try:
            if self.use_grpc:
                return self._get_products_grpc(category, search_query)
            else:
                return self._get_products_rest(category, search_query)
                
        except Exception as e:
            self.logger.error(f"Product catalog error: {e}")
            # Only fall back to minimal mock data if server is completely unavailable
            return self._get_emergency_fallback_products(category)
    
    def _get_products_rest(self, category: str = None, search_query: str = None) -> List[Dict]:
        """REST API approach - Updated to use enhanced server response"""
        try:
            url = f"{self.catalog_service_url}/products"
            params = {}
            
            if category:
                params['category'] = category
            if search_query:
                params['search'] = search_query
            
            # Add simple flag to get just products array instead of metadata wrapper
            params['simple'] = 'true'
            
            self.logger.info(f"Fetching products from {url} with params: {params}")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            products = response.json()
            
            # Handle both simple array response and metadata wrapper
            if isinstance(products, dict) and 'products' in products:
                products = products['products']
            
            self.logger.info(f"Retrieved {len(products)} products from server")
            return products
            
        except Exception as e:
            self.logger.error(f"REST API error: {e}")
            raise
    
    def _get_products_grpc(self, category: str = None, search_query: str = None) -> List[Dict]:
        """gRPC approach - fallback to REST for now"""
        try:
            # For now, fallback to REST - can implement gRPC later if needed
            return self._get_products_rest(category, search_query)
            
        except Exception as e:
            self.logger.error(f"gRPC error: {e}")
            raise
    
    def _get_emergency_fallback_products(self, category: str = None) -> List[Dict]:
        """Minimal emergency fallback when server is completely unavailable"""
        self.logger.warning("Using emergency fallback products - server unavailable")
        
        emergency_products = [
            {
                'id': 'FALLBACK_001',
                'name': 'Basic T-Shirt',
                'description': 'Simple cotton t-shirt (fallback item - server unavailable)',
                'picture': '/static/img/products/fallback-tshirt.jpg',
                'priceUsd': {'currency_code': 'USD', 'units': 25, 'nanos': 0},
                'categories': ['clothing', 'casual', 'fallback']
            },
            {
                'id': 'FALLBACK_002',
                'name': 'Universal Jacket',
                'description': 'All-weather jacket (fallback item - server unavailable)',
                'picture': '/static/img/products/fallback-jacket.jpg',
                'priceUsd': {'currency_code': 'USD', 'units': 89, 'nanos': 0},
                'categories': ['clothing', 'outerwear', 'all-weather', 'fallback']
            },
            {
                'id': 'FALLBACK_003',
                'name': 'Travel Accessory',
                'description': 'Basic travel accessory (fallback item - server unavailable)',
                'picture': '/static/img/products/fallback-accessory.jpg',
                'priceUsd': {'currency_code': 'USD', 'units': 35, 'nanos': 0},
                'categories': ['accessories', 'travel', 'fallback']
            }
        ]
        
        # Add price_usd for backward compatibility
        for product in emergency_products:
            product['price_usd'] = product['priceUsd']
        
        # Filter by category if specified
        if category:
            category_lower = category.lower()
            emergency_products = [p for p in emergency_products 
                                if any(category_lower in cat.lower() for cat in p.get('categories', []))]
        
        return emergency_products

    def get_products_with_filters(self, category: str = None, climate: str = None, 
                                cultural: str = None, exclude_inappropriate: bool = False,
                                price_min: float = None, price_max: float = None) -> List[Dict]:
        """
        Get products using enhanced server filtering capabilities
        """
        try:
            url = f"{self.catalog_service_url}/products"
            params = {'simple': 'true'}  # Get simple array response
            
            if category:
                params['category'] = category
            if climate:
                params['climate'] = climate
            if cultural:
                params['cultural'] = cultural
            if exclude_inappropriate:
                params['exclude_inappropriate'] = 'true'
            if price_min is not None:
                params['price_min'] = price_min
            if price_max is not None:
                params['price_max'] = price_max
            
            self.logger.info(f"Fetching filtered products with params: {params}")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            products = response.json()
            
            # Handle both simple array response and metadata wrapper
            if isinstance(products, dict) and 'products' in products:
                products = products['products']
            
            self.logger.info(f"Retrieved {len(products)} filtered products")
            return products
            
        except Exception as e:
            self.logger.error(f"Error getting filtered products: {e}")
            # Fall back to basic get_products
            return self.get_products(category=category)

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
            # Use enhanced server climate filtering if available
            climate_keywords = self._get_climate_keywords_for_region(country, city, month)
            
            if climate_keywords:
                # Try to use server-side climate filtering
                climate_filtered = self.get_products_with_filters(climate=climate_keywords.get('climate_type'))
                if climate_filtered:
                    self.logger.info(f"Used server-side climate filtering for {city}, {country}")
                    return climate_filtered[:10]
            
            # Fall back to local filtering
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
    
    def _get_climate_keywords_for_region(self, country: str, city: str = None, month: str = None) -> Dict[str, str]:
        """Get climate keywords for server-side filtering based on region"""
        # Simple mapping - could be enhanced with more sophisticated logic
        climate_mapping = {
            'pakistan': {
                'karachi': {'summer': 'hot', 'winter': 'mild'},
                'lahore': {'summer': 'hot', 'winter': 'cold'},
                'skardu': {'summer': 'mild', 'winter': 'cold'},
                'default': {'summer': 'hot', 'winter': 'mild'}
            },
            'japan': {
                'tokyo': {'summer': 'hot', 'winter': 'cold'},
                'default': {'summer': 'mild', 'winter': 'cold'}
            },
            'dubai': {
                'default': {'summer': 'hot', 'winter': 'mild'}
            },
            'turkey': {
                'istanbul': {'summer': 'hot', 'winter': 'mild'},
                'default': {'summer': 'hot', 'winter': 'mild'}
            }
        }
        
        country_key = country.lower()
        if country_key in climate_mapping:
            country_data = climate_mapping[country_key]
            city_key = city.lower() if city else 'default'
            city_data = country_data.get(city_key, country_data.get('default', {}))
            
            # Determine season from month
            if month:
                month_lower = month.lower()
                if month_lower in ['december', 'january', 'february']:
                    season = 'winter'
                elif month_lower in ['june', 'july', 'august']:
                    season = 'summer'
                else:
                    season = 'mild'
                
                climate_type = city_data.get(season, 'mild')
                return {'climate_type': climate_type, 'season': season}
        
        return {}
    
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
            # Try to use enhanced server filtering for destinations
            cultural_filter = None
            climate_filter = None
            
            # Map destinations to cultural filters
            destination_lower = destination.lower()
            if any(place in destination_lower for place in ['pakistan', 'saudi', 'iran', 'dubai']):
                cultural_filter = 'conservative'
            elif any(place in destination_lower for place in ['japan', 'korea']):
                cultural_filter = 'traditional'
            
            # Map to climate filters based on weather data
            if weather_data and weather_data.get('forecasts'):
                avg_temp = sum(f.get('temperature', 20) for f in weather_data['forecasts']) / len(weather_data['forecasts'])
                if avg_temp > 25:
                    climate_filter = 'hot'
                elif avg_temp < 10:
                    climate_filter = 'cold'
                else:
                    climate_filter = 'mild'
            
            # Use enhanced server filtering
            if cultural_filter or climate_filter:
                filtered_products = self.get_products_with_filters(
                    category=category,
                    climate=climate_filter,
                    cultural=cultural_filter,
                    exclude_inappropriate=cultural_filter == 'conservative'
                )
                if filtered_products:
                    return filtered_products
            
            # Fall back to basic products with weather filtering
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
            return self.get_products(category=category)[:5]
    
    def calculate_total_price(self, product_ids: List[str]) -> str:
        """
        Calculate the total price of a list of products by their IDs
        """
        try:
            products = self.get_products()
            total_units = 0
            total_nanos = 0
            
            for product in products:
                if product.get('id') in product_ids:
                    price_usd = product.get('priceUsd', {})
                    total_units += price_usd.get('units', 0)
                    total_nanos += price_usd.get('nanos', 0)
            
            # Convert nanos to dollars and add to units
            total_dollars = total_units + (total_nanos / 1_000_000_000)
            
            return f"${total_dollars:.2f}"
            
        except Exception as e:
            self.logger.error(f"Error calculating total price: {e}")
            return "$0.00"
    
    def get_culturally_relevant_products(self, category: str = None, cultural_context: Dict = None, 
                                       destination: str = None, month: str = None) -> List[Dict]:
        """
        Get products that are culturally appropriate for the destination and time
        """
        try:
            # Use enhanced server filtering for cultural relevance
            cultural_filter = self._determine_cultural_filter(destination, cultural_context)
            exclude_inappropriate = cultural_filter == 'conservative'
            
            # Get products using server-side filtering
            filtered_products = self.get_products_with_filters(
                category=category,
                cultural=cultural_filter,
                exclude_inappropriate=exclude_inappropriate
            )
            
            if filtered_products:
                # Add cultural relevance scores
                for product in filtered_products:
                    product["cultural_score"] = self._calculate_cultural_relevance_score(
                        product, cultural_context, destination, month
                    )
                
                # Sort by cultural relevance
                filtered_products.sort(key=lambda x: x.get("cultural_score", 0), reverse=True)
                
                return filtered_products[:8]  # Return top 8 culturally relevant products
            
            # Fall back to basic filtering if server filtering fails
            products = self.get_products(category=category)
            return self._apply_cultural_filtering_locally(products, cultural_context, destination, month)
            
        except Exception as e:
            self.logger.error(f"Error getting culturally relevant products: {e}")
            return self.get_products(category=category)[:8]
    
    def _determine_cultural_filter(self, destination: str, cultural_context: Dict = None) -> str:
        """Determine appropriate cultural filter based on destination"""
        if not destination:
            return None
            
        destination_lower = destination.lower()
        
        # Conservative destinations
        if any(place in destination_lower for place in ['pakistan', 'saudi', 'iran', 'afghanistan']):
            return 'conservative'
        elif any(place in destination_lower for place in ['dubai', 'turkey', 'malaysia']):
            return 'modest'
        elif any(place in destination_lower for place in ['japan', 'korea', 'thailand']):
            return 'traditional'
        elif any(place in destination_lower for place in ['india', 'nepal', 'tibet']):
            return 'traditional'
        else:
            return 'modest'  # Default to modest for unknown destinations
    
    def _apply_cultural_filtering_locally(self, products: List[Dict], cultural_context: Dict, 
                                        destination: str, month: str = None) -> List[Dict]:
        """Apply cultural filtering locally when server filtering is not available"""
        filtered_products = []
        
        for product in products:
            product_name = product.get("name", "").lower()
            product_description = product.get("description", "").lower()
            categories = [cat.lower() for cat in product.get("categories", [])]
            
            # Cultural appropriateness score
            score = self._calculate_cultural_relevance_score(product, cultural_context, destination, month)
            
            if score > 0.3:  # Only include products with decent cultural relevance
                product_copy = product.copy()
                product_copy["cultural_score"] = score
                filtered_products.append(product_copy)
        
        # Sort by cultural relevance
        filtered_products.sort(key=lambda x: x.get("cultural_score", 0), reverse=True)
        
        return filtered_products[:8]
    
    def _calculate_cultural_relevance_score(self, product: Dict, cultural_context: Dict, 
                                          destination: str, month: str = None) -> float:
        """
        Calculate how culturally relevant a product is for the given context
        """
        score = 0.5  # Base score
        
        product_name = product.get("name", "").lower()
        categories = [cat.lower() for cat in product.get("categories", [])]
        
        # Check for inappropriate items first
        if any('inappropriate' in cat for cat in categories):
            return 0.0  # Immediately exclude inappropriate items
        
        # Boost for culturally appropriate categories
        if any(cat in categories for cat in ['modest', 'conservative', 'traditional']):
            score += 0.3
        
        # Check clothing norms if available
        if cultural_context and cultural_context.get("clothing_norms"):
            clothing_norms = cultural_context["clothing_norms"]
            
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
        
        # Festival-specific relevance
        if cultural_context and cultural_context.get("festivals"):
            festivals = cultural_context["festivals"]
            for festival in festivals:
                festival_name = festival.get("name", "").lower()
                shopping_relevance = festival.get("shopping_relevance", "").lower()
                
                # Check if product matches festival shopping suggestions
                if any(keyword in shopping_relevance for keyword in ["clothing", "attire", "wear"]):
                    if "traditional" in shopping_relevance and "traditional" in product_name:
                        score += 0.4
                    elif "festive" in shopping_relevance and any(word in product_name for word in ["colorful", "bright", "party"]):
                        score += 0.3
        
        return max(0.0, min(1.0, score))
# cultural_data.py - Cultural Data Manager with MCP Implementation
"""
Cultural Data Manager implementing Model Context Protocol (MCP)
Provides culturally sensitive data and filters for AI responses
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import requests
from urllib.parse import quote

class CulturalDataManager:
    """
    Manages cultural data and implements MCP filtering for ethical AI responses
    Enhanced with generic worldwide climate data support
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize cache file path first
        self.cache_file = os.path.join(os.path.dirname(__file__), "climate_cache.json")
        
        # Load cultural data
        self.cultural_database = self._load_cultural_database()
        self.mcp_filters = self._load_mcp_filters()
        
        # Initialize climate data cache
        self.climate_cache = self._load_climate_cache()
        
        # Load cultural taboos and restrictions
        self.cultural_taboos = self._load_cultural_taboos()
        self.clothing_restrictions = self._load_clothing_restrictions()
        
        self.logger.info("Cultural Data Manager initialized with MCP filters, climate cache, and cultural taboos")
    
    def _load_climate_cache(self) -> Dict[str, Any]:
        """Load climate data cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # Clean expired cache entries (older than 30 days)
                current_time = datetime.now()
                cleaned_cache = {}
                
                for key, entry in cache_data.items():
                    if 'timestamp' in entry:
                        entry_time = datetime.fromisoformat(entry['timestamp'])
                        if (current_time - entry_time).days < 30:
                            cleaned_cache[key] = entry
                
                # Save cleaned cache
                if len(cleaned_cache) != len(cache_data):
                    self._save_climate_cache(cleaned_cache)
                
                self.logger.info(f"Loaded climate cache with {len(cleaned_cache)} entries")
                return cleaned_cache
            else:
                self.logger.info("No climate cache file found, starting fresh")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error loading climate cache: {e}")
            return {}
    
    def _save_climate_cache(self, cache_data: Dict[str, Any]):
        """Save climate data cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Saved climate cache with {len(cache_data)} entries")
        except Exception as e:
            self.logger.error(f"Error saving climate cache: {e}")
    
    def _get_cached_climate_data(self, city: str, country: str) -> Optional[Dict[str, Any]]:
        """Get climate data from cache if available and not expired"""
        cache_key = f"{city.lower()}_{country.lower()}"
        
        if cache_key in self.climate_cache:
            entry = self.climate_cache[cache_key]
            
            # Check if entry is still valid (not older than 7 days for dynamic data)
            if 'timestamp' in entry:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if (datetime.now() - entry_time).days < 7:
                    self.logger.info(f"Retrieved climate data from cache for {city}, {country}")
                    return entry['data']
                else:
                    # Remove expired entry
                    del self.climate_cache[cache_key]
                    self._save_climate_cache(self.climate_cache)
        
        return None
    
    def _cache_climate_data(self, city: str, country: str, data: Dict[str, Any]):
        """Cache climate data with timestamp"""
        cache_key = f"{city.lower()}_{country.lower()}"
        
        self.climate_cache[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self._save_climate_cache(self.climate_cache)
        self.logger.info(f"Cached climate data for {city}, {country}")
    
    def _load_cultural_database(self) -> Dict[str, Any]:
        """Load cultural database with festivals, norms, and guidelines"""
        return {
            "Turkey": {
                "clothing_norms": {
                    "general": "Conservative dress recommended, especially in religious areas",
                    "religious_sites": "Cover shoulders and legs, bring head covering for mosques",
                    "business": "Formal attire expected, conservative styling",
                    "casual": "Smart casual acceptable in tourist areas"
                },
                "festivals": [
                    {
                        "name": "Republic Day",
                        "date": "October 29",
                        "significance": "National holiday celebrating Turkish Republic",
                        "shopping_relevance": "Turkish flag themed items, patriotic gifts"
                    },
                    {
                        "name": "Ramadan",
                        "date": "Variable lunar calendar",
                        "significance": "Holy month of fasting",
                        "shopping_relevance": "Modest clothing, dates, traditional sweets"
                    }
                ],
                "seasonal_info": {
                    "october": {
                        "weather": "Mild autumn weather, 15-22°C",
                        "clothing": "Layers recommended, light jackets for evenings"
                    }
                },
                "taboos": ["revealing clothing in religious areas", "leather products during religious festivals"],
                "gift_culture": "Hospitality gifts appreciated, avoid alcohol unless certain of recipient"
            },
            
            "Dubai": {
                "clothing_norms": {
                    "general": "Modest dress code, respect for Islamic customs",
                    "religious_sites": "Full coverage required, bring appropriate attire",
                    "business": "Conservative formal wear, long sleeves recommended",
                    "casual": "Resort areas more relaxed, but still modest"
                },
                "festivals": [
                    {
                        "name": "Eid al-Fitr",
                        "date": "Variable lunar calendar", 
                        "significance": "End of Ramadan celebrations",
                        "shopping_relevance": "Festive clothing, gold jewelry, dates, traditional sweets"
                    },
                    {
                        "name": "Dubai Shopping Festival",
                        "date": "January-February",
                        "significance": "Annual shopping and entertainment festival",
                        "shopping_relevance": "Discounts, special promotions, cultural events"
                    }
                ],
                "taboos": ["revealing clothing", "pork products", "alcohol gifts without certainty"],
                "gift_culture": "Gold jewelry popular, luxury items appreciated, halal food items"
            },
            
            "Japan": {
                "clothing_norms": {
                    "general": "Neat, conservative appearance valued",
                    "religious_sites": "Remove shoes, modest dress",
                    "business": "Formal dark suits, attention to detail important",
                    "casual": "Clean, well-coordinated outfits preferred"
                },
                "festivals": [
                    {
                        "name": "Cherry Blossom Season",
                        "date": "March-May",
                        "significance": "Traditional hanami flower viewing",
                        "shopping_relevance": "Picnic supplies, traditional clothing, photography gear"
                    },
                    {
                        "name": "Golden Week",
                        "date": "Late April-Early May",
                        "significance": "Collection of national holidays",
                        "shopping_relevance": "Travel gear, traditional crafts, souvenirs"
                    }
                ],
                "taboos": ["loud colors in business settings", "shoes indoors"],
                "gift_culture": "Omiyage (souvenir gifts) expected, presentation important"
            },
            
            "Pakistan": {
                "clothing_norms": {
                    "general": "Conservative dress, traditional clothing appreciated",
                    "religious_sites": "Modest coverage required, head covering for women",
                    "business": "Formal attire, cultural sensitivity important",
                    "casual": "Traditional shalwar kameez widely worn and appreciated"
                },
                "festivals": [
                    {
                        "name": "Eid al-Fitr",
                        "date": "Variable lunar calendar",
                        "significance": "End of Ramadan celebrations",
                        "shopping_relevance": "New clothes tradition, sweets, henna, jewelry"
                    },
                    {
                        "name": "Wedding Season",
                        "date": "November-February",
                        "significance": "Peak wedding season",
                        "shopping_relevance": "Formal wear, jewelry, traditional outfits, gifts"
                    }
                ],
                "taboos": ["non-halal food items", "alcohol", "leather during religious periods"],
                "gift_culture": "Hospitality important, traditional crafts valued",
                "regional_climate": {
                    "karachi": {
                        "name": "Karachi",
                        "region": "Coastal Sindh",
                        "climate_type": "Tropical desert",
                        "seasonal_weather": {
                            "january": {"temp_range": "15-25°C", "description": "Mild and pleasant", "clothing": "Light layers, cotton clothing"},
                            "february": {"temp_range": "16-26°C", "description": "Warm and comfortable", "clothing": "Light cotton, short sleeves"},
                            "march": {"temp_range": "20-30°C", "description": "Getting warmer", "clothing": "Light cotton, breathable fabrics"},
                            "april": {"temp_range": "24-34°C", "description": "Hot spring", "clothing": "Light cotton, loose clothing"},
                            "may": {"temp_range": "27-37°C", "description": "Very hot", "clothing": "Light cotton, sun protection"},
                            "june": {"temp_range": "28-38°C", "description": "Peak summer heat", "clothing": "Light cotton, cooling fabrics"},
                            "july": {"temp_range": "29-35°C", "description": "Hot with humidity", "clothing": "Light cotton, moisture-wicking"},
                            "august": {"temp_range": "28-34°C", "description": "Hot and humid", "clothing": "Light cotton, breathable"},
                            "september": {"temp_range": "26-32°C", "description": "Still warm", "clothing": "Light cotton, transitional"},
                            "october": {"temp_range": "22-30°C", "description": "Pleasant autumn", "clothing": "Light layers"},
                            "november": {"temp_range": "18-26°C", "description": "Cooling down", "clothing": "Light jacket, long sleeves"},
                            "december": {"temp_range": "14-22°C", "description": "Cool winter", "clothing": "Light jacket, warm layers"}
                        }
                    },
                    "lahore": {
                        "name": "Lahore",
                        "region": "Punjab Plains",
                        "climate_type": "Subtropical",
                        "seasonal_weather": {
                            "january": {"temp_range": "8-18°C", "description": "Cool winter", "clothing": "Warm layers, light jacket"},
                            "february": {"temp_range": "10-22°C", "description": "Mild spring-like", "clothing": "Light layers, sweater"},
                            "march": {"temp_range": "15-27°C", "description": "Warm spring", "clothing": "Light jacket, cotton"},
                            "april": {"temp_range": "20-33°C", "description": "Hot spring", "clothing": "Light cotton, sun hat"},
                            "may": {"temp_range": "25-38°C", "description": "Very hot", "clothing": "Light cotton, sun protection"},
                            "june": {"temp_range": "28-40°C", "description": "Peak summer heat", "clothing": "Light cotton, cooling fabrics"},
                            "july": {"temp_range": "29-36°C", "description": "Hot with monsoon", "clothing": "Light cotton, rain protection"},
                            "august": {"temp_range": "28-35°C", "description": "Hot and humid", "clothing": "Light cotton, breathable"},
                            "september": {"temp_range": "25-32°C", "description": "Still warm", "clothing": "Light cotton, transitional"},
                            "october": {"temp_range": "18-28°C", "description": "Pleasant autumn", "clothing": "Light layers"},
                            "november": {"temp_range": "12-22°C", "description": "Cooling down", "clothing": "Light jacket, long sleeves"},
                            "december": {"temp_range": "8-16°C", "description": "Cold winter", "clothing": "Warm jacket, layers"}
                        }
                    },
                    "islamabad": {
                        "name": "Islamabad",
                        "region": "Northern Pakistan",
                        "climate_type": "Subtropical highland",
                        "seasonal_weather": {
                            "january": {"temp_range": "3-12°C", "description": "Cold winter", "clothing": "Warm coat, layers, scarf"},
                            "february": {"temp_range": "5-15°C", "description": "Cool spring", "clothing": "Warm layers, light jacket"},
                            "march": {"temp_range": "10-20°C", "description": "Mild spring", "clothing": "Light jacket, long sleeves"},
                            "april": {"temp_range": "15-25°C", "description": "Warm spring", "clothing": "Light layers, cotton"},
                            "may": {"temp_range": "20-30°C", "description": "Hot spring", "clothing": "Light cotton, sun protection"},
                            "june": {"temp_range": "23-33°C", "description": "Warm summer", "clothing": "Light cotton, breathable"},
                            "july": {"temp_range": "22-31°C", "description": "Warm with rain", "clothing": "Light layers, rain jacket"},
                            "august": {"temp_range": "21-30°C", "description": "Warm and humid", "clothing": "Light cotton, moisture-wicking"},
                            "september": {"temp_range": "18-27°C", "description": "Pleasant autumn", "clothing": "Light layers"},
                            "october": {"temp_range": "12-22°C", "description": "Cool autumn", "clothing": "Light jacket, long sleeves"},
                            "november": {"temp_range": "7-17°C", "description": "Cold autumn", "clothing": "Warm layers, jacket"},
                            "december": {"temp_range": "3-11°C", "description": "Very cold winter", "clothing": "Heavy coat, warm layers"}
                        }
                    },
                    "skardu": {
                        "name": "Skardu",
                        "region": "Northern Areas",
                        "climate_type": "Cold desert",
                        "seasonal_weather": {
                            "january": {"temp_range": "-10-5°C", "description": "Very cold winter", "clothing": "Heavy winter coat, thermal layers, gloves"},
                            "february": {"temp_range": "-8-7°C", "description": "Cold winter", "clothing": "Heavy coat, multiple layers, warm hat"},
                            "march": {"temp_range": "-2-12°C", "description": "Cold spring", "clothing": "Heavy jacket, warm layers"},
                            "april": {"temp_range": "3-18°C", "description": "Cool spring", "clothing": "Warm jacket, layers"},
                            "may": {"temp_range": "8-23°C", "description": "Mild spring", "clothing": "Light jacket, long sleeves"},
                            "june": {"temp_range": "12-28°C", "description": "Warm summer", "clothing": "Light layers, cotton"},
                            "july": {"temp_range": "15-25°C", "description": "Cool summer", "clothing": "Light jacket, long sleeves"},
                            "august": {"temp_range": "14-24°C", "description": "Cool summer", "clothing": "Light jacket, layers"},
                            "september": {"temp_range": "8-20°C", "description": "Cool autumn", "clothing": "Warm layers, jacket"},
                            "october": {"temp_range": "0-12°C", "description": "Cold autumn", "clothing": "Heavy jacket, thermal layers"},
                            "november": {"temp_range": "-5-5°C", "description": "Very cold", "clothing": "Heavy coat, multiple layers"},
                            "december": {"temp_range": "-12-2°C", "description": "Extremely cold", "clothing": "Heavy winter coat, thermal base layers"}
                        }
                    }
                }
            },
            
            "India": {
                "clothing_norms": {
                    "general": "Varies by region, generally conservative",
                    "religious_sites": "Modest dress required, remove shoes",
                    "business": "Formal wear, cultural awareness appreciated", 
                    "casual": "Traditional and western both acceptable"
                },
                "festivals": [
                    {
                        "name": "Diwali",
                        "date": "October-November",
                        "significance": "Festival of lights",
                        "shopping_relevance": "Traditional clothing, jewelry, sweets, decorative items"
                    },
                    {
                        "name": "Holi",
                        "date": "March",
                        "significance": "Festival of colors",
                        "shopping_relevance": "White clothing, colors, water guns, sweets"
                    }
                ],
                "taboos": ["leather products for Hindu temples", "beef products"],
                "gift_culture": "Sweets popular, traditional items appreciated"
            }
        }
    
    def _load_mcp_filters(self) -> Dict[str, Any]:
        """Load MCP (Model Context Protocol) filters for ethical AI"""
        return {
            "sensitivity_checks": {
                "religious_appropriateness": [
                    "Check for religious symbol misuse",
                    "Ensure dietary restrictions respected", 
                    "Avoid religious stereotypes"
                ],
                "cultural_respect": [
                    "Avoid cultural appropriation suggestions",
                    "Respect traditional dress codes",
                    "Consider local sensitivities"
                ],
                "gender_inclusivity": [
                    "Provide options for all genders",
                    "Respect local gender norms without imposing",
                    "Avoid gendered assumptions"
                ]
            },
            "content_filters": {
                "prohibited_suggestions": [
                    "Items that mock cultural practices",
                    "Inappropriate religious imagery",
                    "Culturally insensitive costumes"
                ],
                "warning_categories": [
                    "alcohol_related",
                    "religious_symbols", 
                    "traditional_clothing_for_outsiders",
                    "sacred_items"
                ]
            },
            "recommendation_guidelines": {
                "always_include": [
                    "Respectful alternatives",
                    "Cultural context explanation",
                    "Local etiquette tips"
                ],
                "prioritize": [
                    "Locally made products",
                    "Culturally appropriate items",
                    "Educational value"
                ]
            }
        }
    
    def _load_cultural_taboos(self) -> Dict[str, Dict[str, Any]]:
        """Load cultural taboos and restrictions by country/region"""
        return {
            "pakistan": {
                "clothing_taboos": ["bikini", "revealing swimwear", "short shorts", "crop tops", "low-cut tops"],
                "beach_appropriate": ["modest swimwear", "full coverage swimsuit", "burkini", "long sleeve rashguard"],
                "religious_considerations": ["modest necklines", "covered arms", "covered legs"],
                "cultural_priorities": ["shalwar kameez", "dupatta", "traditional wear"]
            },
            "saudi arabia": {
                "clothing_taboos": ["bikini", "revealing clothing", "short sleeves", "shorts", "tight clothing"],
                "mandatory": ["abaya", "modest dress", "covered clothing"],
                "religious_considerations": ["full coverage", "loose fitting"],
                "cultural_priorities": ["traditional saudi dress", "modest fashion"]
            },
            "iran": {
                "clothing_taboos": ["bikini", "short sleeves", "revealing clothing", "tight jeans"],
                "mandatory": ["hijab", "modest dress", "covered arms and legs"],
                "religious_considerations": ["head covering", "loose clothing"],
                "cultural_priorities": ["traditional persian dress", "modest fashion"]
            },
            "india": {
                "clothing_taboos": ["very revealing clothing", "inappropriate temple wear"],
                "temple_appropriate": ["covered shoulders", "long pants", "modest dress"],
                "cultural_priorities": ["saree", "salwar kameez", "traditional indian wear"],
                "regional_variations": True
            },
            "japan": {
                "clothing_taboos": ["overly casual in formal settings", "shoes in sacred spaces"],
                "cultural_priorities": ["kimono", "yukata", "business formal"],
                "seasonal_considerations": ["appropriate seasonal colors", "formal occasions"]
            },
            "uae": {
                "clothing_taboos": ["very revealing clothing", "inappropriate mosque wear"],
                "mosque_appropriate": ["covered arms and legs", "modest dress", "head covering"],
                "cultural_priorities": ["traditional emirati dress", "business formal"],
                "tourist_areas_relaxed": True
            }
        }
    
    def _load_clothing_restrictions(self) -> Dict[str, Dict[str, Any]]:
        """Load clothing restrictions by location type and season"""
        return {
            "religious_sites": {
                "mosques": ["covered arms and legs", "head covering for women", "modest dress", "no shoes"],
                "temples": ["covered shoulders", "long pants", "modest dress", "no leather"],
                "churches": ["covered shoulders", "modest dress", "respectful attire"]
            },
            "public_beaches": {
                "conservative_countries": ["modest swimwear", "cover-ups", "burkini"],
                "liberal_countries": ["standard swimwear", "bikini allowed", "casual beachwear"]
            },
            "business_settings": {
                "formal": ["business suit", "formal dress", "conservative colors"],
                "casual": ["business casual", "smart casual", "appropriate footwear"]
            }
        }
    
    def get_cultural_data(self, destination: str, month: str = None, city: str = None) -> Dict[str, Any]:
        """Get cultural data for a destination, enhanced with Wikipedia data and regional variations"""
        
        # Normalize destination name
        destination = self._normalize_destination(destination)
        city = city.lower() if city else None
        
        if destination in self.cultural_database:
            data = self.cultural_database[destination].copy()
            
            # Handle regional climate data if city is specified
            if city and "regional_climate" in data and city in data["regional_climate"]:
                regional_data = data["regional_climate"][city]
                data["regional_info"] = regional_data
                
                # Override seasonal info with regional data if month is specified
                if month and month.lower() in regional_data.get("seasonal_weather", {}):
                    month_weather = regional_data["seasonal_weather"][month.lower()]
                    data["current_season"] = {
                        "weather": month_weather["description"],
                        "clothing": month_weather["clothing"],
                        "temperature": month_weather["temp_range"]
                    }
                    self.logger.info(f"Applied regional climate data for {city}, {destination} in {month}")
            
            # Add current seasonal info if available and no regional override
            if "current_season" not in data:
                current_month = datetime.now().strftime("%B").lower()
                if "seasonal_info" in data and current_month in data["seasonal_info"]:
                    data["current_season"] = data["seasonal_info"][current_month]
            
            # Enhance with Wikipedia data for festivals
            if month:
                wiki_festivals = self.get_festivals_from_wikipedia(destination, month)
                if wiki_festivals:
                    # Merge with existing festivals
                    existing_festivals = data.get("festivals", [])
                    data["festivals"] = existing_festivals + wiki_festivals
            
            self.logger.info(f"Retrieved cultural data for {destination}" + (f" ({city})" if city else ""))
            return data
        else:
            # Try to fetch from Wikipedia for unknown destinations
            self.logger.info(f"Fetching cultural data from Wikipedia for {destination}")
            
            wiki_cultural = self.get_cultural_norms_from_wikipedia(destination)
            wiki_festivals = []
            if month:
                wiki_festivals = self.get_festivals_from_wikipedia(destination, month)
            
            # Combine with fallback data
            fallback_data = {
                "clothing_norms": {
                    "general": "Respectful, modest dress recommended",
                    "religious_sites": "Conservative clothing advised",
                    "business": "Formal attire appropriate",
                    "casual": "Smart casual recommended"
                },
                "festivals": [],
                "taboos": [],
                "gift_culture": "Research local customs for gift-giving",
                "note": f"Cultural data fetched from Wikipedia for {destination}"
            }
            
            # Merge Wikipedia data
            if wiki_cultural.get("clothing_norms"):
                fallback_data["clothing_norms"].update(wiki_cultural["clothing_norms"])
            if wiki_cultural.get("etiquette"):
                fallback_data["etiquette"] = wiki_cultural["etiquette"]
            if wiki_cultural.get("taboos"):
                fallback_data["taboos"] = wiki_cultural["taboos"]
            
            fallback_data["festivals"] = wiki_festivals
            
            return fallback_data
    
    def get_regional_climate_data(self, country: str, city: str, month: str = None) -> Optional[Dict[str, Any]]:
        """Get specific regional climate data for a city within a country - Generic for any city worldwide"""
        country = self._normalize_destination(country)
        city = city.lower() if city else None
        
        if not city:
            return None
            
        # First, check cache
        cached_data = self._get_cached_climate_data(city, country)
        if cached_data:
            # Add current month data if requested
            if month and month.lower() in cached_data.get("seasonal_weather", {}):
                cached_data["current_month_weather"] = cached_data["seasonal_weather"][month.lower()]
            return cached_data
        
        # Second, try to get from static database (for Pakistan and other manually added cities)
        if country in self.cultural_database:
            regional_climate = self.cultural_database[country].get("regional_climate", {})
            if city in regional_climate:
                city_data = regional_climate[city].copy()
                
                # Add month-specific data if requested
                if month and month.lower() in city_data.get("seasonal_weather", {}):
                    month_data = city_data["seasonal_weather"][month.lower()]
                    city_data["current_month_weather"] = month_data
                
                # Cache the data
                self._cache_climate_data(city, country, city_data)
                
                self.logger.info(f"Retrieved regional climate data for {city}, {country}")
                return city_data
        
        # Third, try to fetch from Wikipedia
        self.logger.info(f"Fetching climate data from Wikipedia for {city}, {country}")
        wiki_climate_data = self._get_climate_data_from_wikipedia(city, country, month)
        if wiki_climate_data:
            # Cache the data
            self._cache_climate_data(city, country, wiki_climate_data)
            return wiki_climate_data
            
        # Fourth, final fallback - try weather API
        self.logger.info(f"Trying weather API fallback for {city}, {country}")
        weather_api_data = self._get_climate_data_from_weather_api(city, country, month)
        if weather_api_data:
            # Cache the data
            self._cache_climate_data(city, country, weather_api_data)
            return weather_api_data
        
        self.logger.warning(f"No climate data found for {city}, {country} from any source")
        return None
    
    def get_cultural_travel_recommendations(self, country: str, city: str = None, month: str = None, 
                                          activity: str = None) -> Dict[str, Any]:
        """Get comprehensive cultural travel recommendations with taboo filtering
        
        Workflow: Country (mandatory) → Month (festivals) → Location (climate) → Activity (context)
        Returns hierarchical recommendations: Cultural dress → Regional dress → General clothing
        """
        country = self._normalize_destination(country)
        
        # Initialize response structure
        response = {
            "country": country,
            "city": city,
            "month": month,
            "activity": activity,
            "cultural_data": {},
            "climate_data": {},
            "festivals": [],
            "recommendations": {
                "cultural_priority": [],
                "regional_appropriate": [],
                "general_suitable": [],
                "taboos_to_avoid": [],
                "special_considerations": []
            },
            "filters_applied": []
        }
        
        try:
            # 1. Get cultural norms and taboos for the country
            cultural_data = self._get_country_cultural_data(country)
            response["cultural_data"] = cultural_data
            
            # 2. Apply cultural taboo filters
            taboos = self._get_cultural_taboos(country, activity)
            response["recommendations"]["taboos_to_avoid"] = taboos
            response["filters_applied"].append("cultural_taboos")
            
            # 3. Get climate data if city is provided
            if city:
                climate_data = self.get_regional_climate_data(country, city, month)
                if climate_data:
                    response["climate_data"] = climate_data
                    response["filters_applied"].append("climate_appropriate")
            
            # 4. Get festivals if month is provided (30-day window)
            festivals = []
            if month:
                festivals = self._get_festivals_in_window(country, month, city)
                response["festivals"] = festivals
                if festivals:
                    response["filters_applied"].append("festival_appropriate")
            
            # 5. Generate hierarchical clothing recommendations
            recommendations = self._generate_hierarchical_recommendations(
                country, city, month, activity, cultural_data, 
                response.get("climate_data"), festivals, taboos
            )
            response["recommendations"].update(recommendations)
            
            self.logger.info(f"Generated cultural travel recommendations for {country}" + 
                           (f" ({city})" if city else "") + (f" in {month}" if month else ""))
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating cultural recommendations: {e}")
            return self._get_fallback_recommendations(country, city, month)
    
    def _get_country_cultural_data(self, country: str) -> Dict[str, Any]:
        """Get comprehensive cultural data for a country from Wikipedia"""
        try:
            # Try to get from static database first
            if country in self.cultural_database:
                return self.cultural_database[country]
            
            # Fetch from Wikipedia
            cultural_data = self.get_cultural_norms_from_wikipedia(country)
            if cultural_data:
                return cultural_data
            
            # Fallback to basic structure
            return {
                "clothing_norms": {
                    "conservative": True,
                    "modesty_required": True
                },
                "cultural_values": ["respect", "modesty", "tradition"],
                "religious_considerations": ["modest dress"]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cultural data for {country}: {e}")
            return {}
    
    def _get_cultural_taboos(self, country: str, activity: str = None) -> List[str]:
        """Get cultural taboos and restrictions for a country/activity"""
        taboos = []
        
        # Normalize country name to lowercase for lookup
        country_lower = country.lower()
        
        # Get country-specific taboos
        if country_lower in self.cultural_taboos:
            country_taboos = self.cultural_taboos[country_lower]
            
            # Add activity-specific restrictions
            if activity:
                activity_lower = activity.lower()
                if "beach" in activity_lower or "swim" in activity_lower:
                    # For beach activities, include all swimwear-related taboos
                    beach_taboos = [item for item in country_taboos.get("clothing_taboos", []) 
                                  if "swimwear" in item or "bikini" in item or "revealing" in item]
                    taboos.extend(beach_taboos)
                    # Also add general beach restrictions
                    taboos.extend(["revealing swimwear", "inappropriate beach attire"])
                elif "religious" in activity_lower or "mosque" in activity_lower or "temple" in activity_lower:
                    taboos.extend(["revealing clothing", "inappropriate religious wear", "uncovered shoulders"])
                else:
                    # For general activities, include basic clothing taboos
                    taboos.extend(country_taboos.get("clothing_taboos", [])[:3])  # Top 3 taboos
            else:
                # No specific activity, include general taboos
                taboos.extend(country_taboos.get("clothing_taboos", [])[:3])  # Top 3 taboos
        
        return list(set(taboos))  # Remove duplicates
    
    def _get_festivals_in_window(self, country: str, month: str, city: str = None) -> List[Dict[str, Any]]:
        """Get festivals within 30-day window of the specified month"""
        try:
            # Get base month festivals
            festivals = self.get_festivals_from_wikipedia(country, month)
            
            # Add city-specific festivals if city is provided
            if city:
                city_festivals = self.get_festivals_from_wikipedia(city, month)
                if city_festivals:
                    festivals.extend(city_festivals)
            
            # Filter for 30-day window and add cultural dress requirements
            enhanced_festivals = []
            for festival in festivals:
                festival_info = {
                    "name": festival.get("name", ""),
                    "date": festival.get("date", ""),
                    "description": festival.get("description", ""),
                    "cultural_dress": self._get_festival_dress_requirements(festival.get("name", ""), country),
                    "significance": festival.get("significance", "")
                }
                enhanced_festivals.append(festival_info)
            
            return enhanced_festivals[:5]  # Limit to top 5 festivals
            
        except Exception as e:
            self.logger.error(f"Error getting festivals for {country} in {month}: {e}")
            return []
    
    def _get_festival_dress_requirements(self, festival_name: str, country: str) -> List[str]:
        """Get specific dress requirements for festivals"""
        festival_lower = festival_name.lower()
        
        # Festival-specific dress codes
        if "eid" in festival_lower or "ramadan" in festival_lower:
            return ["traditional islamic dress", "modest formal wear", "cultural attire"]
        elif "diwali" in festival_lower or "holi" in festival_lower:
            return ["traditional indian wear", "bright colors", "festive clothing"]
        elif "christmas" in festival_lower:
            return ["formal festive wear", "traditional dress", "warm clothing"]
        elif "new year" in festival_lower:
            return ["formal party wear", "traditional celebration dress"]
        elif "basant" in festival_lower or "kite" in festival_lower:
            return ["bright yellow clothing", "traditional wear", "outdoor suitable"]
        
        # Country-specific defaults
        if country in self.cultural_taboos:
            cultural_priorities = self.cultural_taboos[country].get("cultural_priorities", [])
            return cultural_priorities[:3]  # Top 3 cultural priorities
        
        return ["traditional dress", "formal wear", "cultural appropriate"]
    
    def _generate_hierarchical_recommendations(self, country: str, city: str, month: str, 
                                            activity: str, cultural_data: Dict, climate_data: Dict, 
                                            festivals: List, taboos: List) -> Dict[str, List[str]]:
        """Generate hierarchical clothing recommendations
        
        Priority: Cultural dress > Regional dress > General clothing
        """
        recommendations = {
            "cultural_priority": [],
            "regional_appropriate": [],
            "general_suitable": [],
            "special_considerations": []
        }
        
        # 1. Cultural Priority (Traditional/Festival wear + Activity-specific cultural needs)
        if festivals:
            for festival in festivals:
                recommendations["cultural_priority"].extend(festival.get("cultural_dress", []))
        
        # Add country cultural priorities
        country_lower = country.lower()
        if country_lower in self.cultural_taboos:
            cultural_priorities = self.cultural_taboos[country_lower].get("cultural_priorities", [])
            recommendations["cultural_priority"].extend(cultural_priorities)
            
            # Add activity-specific cultural requirements
            if activity:
                activity_lower = activity.lower()
                if "beach" in activity_lower or "swim" in activity_lower:
                    # For beach activities, prioritize culturally appropriate swimwear
                    beach_appropriate = self.cultural_taboos[country_lower].get("beach_appropriate", [])
                    if beach_appropriate:
                        recommendations["cultural_priority"].extend(beach_appropriate)
                elif "religious" in activity_lower or "mosque" in activity_lower or "temple" in activity_lower:
                    # For religious activities, prioritize religious considerations
                    religious_considerations = self.cultural_taboos[country_lower].get("religious_considerations", [])
                    if religious_considerations:
                        recommendations["cultural_priority"].extend(religious_considerations)
        
        # 2. Regional Appropriate (Climate + Local norms)
        if climate_data:
            # Get climate-appropriate clothing
            current_weather = climate_data.get("current_month_weather", {})
            if current_weather:
                clothing = current_weather.get("clothing", "")
                if clothing:
                    recommendations["regional_appropriate"].append(clothing)
            
            # Add regional seasonal clothing
            seasonal_weather = climate_data.get("seasonal_weather", {})
            if month and month.lower() in seasonal_weather:
                month_clothing = seasonal_weather[month.lower()].get("clothing", "")
                if month_clothing:
                    recommendations["regional_appropriate"].append(month_clothing)
        
        # 3. General Suitable (Activity-based)
        if activity:
            activity_clothing = self._get_activity_appropriate_clothing(activity, country)
            recommendations["general_suitable"].extend(activity_clothing)
        
        # Add basic suitable clothing
        recommendations["general_suitable"].extend([
            "comfortable walking shoes", "modest casual wear", "weather appropriate layers"
        ])
        
        # 4. Special Considerations
        if taboos:
            recommendations["special_considerations"].append(f"Avoid: {', '.join(taboos[:3])}")
        
        country_lower = country.lower()
        if country_lower in self.cultural_taboos:
            mandatory = self.cultural_taboos[country_lower].get("mandatory", [])
            if mandatory:
                recommendations["special_considerations"].append(f"Required: {', '.join(mandatory[:2])}")
        
        # Remove duplicates and limit items
        for key in recommendations:
            recommendations[key] = list(set(recommendations[key]))[:5]
        
        return recommendations
    
    def _get_activity_appropriate_clothing(self, activity: str, country: str) -> List[str]:
        """Get clothing appropriate for specific activities"""
        activity_lower = activity.lower()
        
        if "beach" in activity_lower or "swim" in activity_lower:
            # Check cultural restrictions for beach wear
            country_lower = country.lower()
            if country_lower in self.cultural_taboos:
                beach_appropriate = self.cultural_taboos[country_lower].get("beach_appropriate", [])
                if beach_appropriate:
                    return beach_appropriate
            return ["modest swimwear", "beach cover-up", "sun protection"]
        
        elif "business" in activity_lower or "work" in activity_lower:
            return ["business attire", "formal dress", "professional clothing"]
        
        elif "hiking" in activity_lower or "outdoor" in activity_lower:
            return ["outdoor gear", "comfortable hiking boots", "weather protection"]
        
        elif "religious" in activity_lower or "temple" in activity_lower or "mosque" in activity_lower:
            return ["modest religious wear", "covered clothing", "respectful attire"]
        
        elif "party" in activity_lower or "celebration" in activity_lower:
            return ["festive wear", "traditional celebration dress", "formal party attire"]
        
        return ["casual appropriate wear", "comfortable clothing"]
    
    def _get_fallback_recommendations(self, country: str, city: str = None, month: str = None) -> Dict[str, Any]:
        """Provide fallback recommendations when data is unavailable"""
        return {
            "country": country,
            "city": city,
            "month": month,
            "cultural_data": {"conservative": True},
            "climate_data": {},
            "festivals": [],
            "recommendations": {
                "cultural_priority": ["traditional dress", "modest clothing"],
                "regional_appropriate": ["weather appropriate clothing", "comfortable shoes"],
                "general_suitable": ["modest casual wear", "respectful attire"],
                "taboos_to_avoid": ["revealing clothing", "inappropriate cultural wear"],
                "special_considerations": ["Research local customs", "Dress modestly"]
            },
            "filters_applied": ["conservative_fallback"]
        }
        
    def _get_climate_data_from_wikipedia(self, city: str, country: str, month: str = None) -> Optional[Dict[str, Any]]:
        """Scrape climate data from Wikipedia for any city worldwide"""
        try:
            # Try different search terms for the city
            search_terms = [
                f"{city} climate",
                f"Climate of {city}",
                f"{city}, {country} climate",
                f"Weather in {city}"
            ]
            
            for search_term in search_terms:
                try:
                    # Search for climate page
                    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(search_term)}&format=json"
                    response = requests.get(search_url, headers={'User-Agent': 'TravelChatbot/1.0'}, timeout=10)
                    response.raise_for_status()
                    
                    search_results = response.json()
                    
                    if search_results['query']['search']:
                        page_title = search_results['query']['search'][0]['title']
                        
                        # Fetch page content
                        content_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=false&explaintext=true&titles={quote(page_title)}&format=json"
                        content_response = requests.get(content_url, headers={'User-Agent': 'TravelChatbot/1.0'}, timeout=10)
                        content_response.raise_for_status()
                        
                        content_data = content_response.json()
                        pages = content_data['query']['pages']
                        
                        for page_id, page_data in pages.items():
                            if 'extract' in page_data:
                                extract = page_data['extract']
                                
                                # Parse climate data from the extract
                                climate_data = self._parse_wikipedia_climate_data(extract, city, country, month)
                                if climate_data:
                                    self.logger.info(f"Successfully parsed climate data from Wikipedia for {city}")
                                    return climate_data
                                
                except Exception as e:
                    self.logger.warning(f"Failed to fetch climate data for search term '{search_term}': {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error fetching climate data from Wikipedia: {e}")
            
        return None
    
    def _parse_wikipedia_climate_data(self, extract: str, city: str, country: str, month: str = None) -> Optional[Dict[str, Any]]:
        """Parse climate information from Wikipedia extract text"""
        try:
            import re
            
            # Initialize climate data structure
            climate_data = {
                "name": city.title(),
                "region": f"{city.title()}, {country.title()}",
                "climate_type": "Unknown",
                "seasonal_weather": {},
                "source": "Wikipedia"
            }
            
            # Extract temperature patterns (e.g., "25°C", "15–25°C", "15 to 25°C")
            temp_patterns = [
                r'(\d+)[–\-](\d+)\s*°C',  # 15-25°C
                r'(\d+)\s*to\s*(\d+)\s*°C',  # 15 to 25°C
                r'(\d+)\s*°C',  # 25°C
            ]
            
            # Look for monthly climate data
            months = ['january', 'february', 'march', 'april', 'may', 'june', 
                     'july', 'august', 'september', 'october', 'november', 'december']
            
            extract_lower = extract.lower()
            
            # Try to find climate table data or descriptive text
            for month_name in months:
                month_pattern = rf'{month_name}[:\s]*.*?(\d+[–\-]?\d*\s*°C).*?(?:\.|$)'
                match = re.search(month_pattern, extract_lower, re.IGNORECASE)
                
                if match:
                    temp_str = match.group(1).strip()
                    # Create month data
                    avg_temp = self._extract_average_temp(temp_str + "°C") if temp_str else 20
                    
                    climate_data["seasonal_weather"][month_name] = {
                        "temp_range": temp_str + "°C" if temp_str else "15-25°C",
                        "description": self._get_climate_description(avg_temp),
                        "clothing": self._get_clothing_recommendation(avg_temp)
                    }
            
            # If we found some seasonal data, return it
            if climate_data["seasonal_weather"]:
                # Add current month data if requested
                if month and month.lower() in climate_data["seasonal_weather"]:
                    climate_data["current_month_weather"] = climate_data["seasonal_weather"][month.lower()]
                
                return climate_data
            
            # Fallback: Try to extract general climate information
            if "tropical" in extract_lower:
                climate_data["climate_type"] = "Tropical"
            elif "desert" in extract_lower:
                climate_data["climate_type"] = "Desert"
            elif "temperate" in extract_lower:
                climate_data["climate_type"] = "Temperate"
            elif "continental" in extract_lower:
                climate_data["climate_type"] = "Continental"
            
            # If we have climate type, create basic seasonal data
            if climate_data["climate_type"] != "Unknown":
                self._create_basic_seasonal_data(climate_data, climate_data["climate_type"])
                
                if month and month.lower() in climate_data["seasonal_weather"]:
                    climate_data["current_month_weather"] = climate_data["seasonal_weather"][month.lower()]
                
                return climate_data
                
        except Exception as e:
            self.logger.error(f"Error parsing Wikipedia climate data: {e}")
            
        return None
    
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
    
    def _get_climate_description(self, avg_temp: float) -> str:
        """Get climate description based on temperature"""
        if avg_temp < 0:
            return "Very cold winter"
        elif avg_temp < 10:
            return "Cold winter"
        elif avg_temp < 15:
            return "Cool weather"
        elif avg_temp < 20:
            return "Mild weather"
        elif avg_temp < 25:
            return "Warm weather"
        elif avg_temp < 30:
            return "Hot weather"
        else:
            return "Very hot weather"
    
    def _get_clothing_recommendation(self, avg_temp: float) -> str:
        """Get clothing recommendation based on temperature"""
        if avg_temp < 0:
            return "Heavy winter coat, thermal layers, gloves, scarf"
        elif avg_temp < 10:
            return "Heavy coat, warm layers, warm hat"
        elif avg_temp < 15:
            return "Warm jacket, layers, long sleeves"
        elif avg_temp < 20:
            return "Light jacket, long sleeves, layers"
        elif avg_temp < 25:
            return "Light layers, cotton clothing"
        elif avg_temp < 30:
            return "Light cotton, breathable fabrics"
        else:
            return "Light cotton, sun protection, cooling fabrics"
    
    def _create_basic_seasonal_data(self, climate_data: Dict[str, Any], climate_type: str):
        """Create basic seasonal weather data based on climate type"""
        months = ['january', 'february', 'march', 'april', 'may', 'june', 
                 'july', 'august', 'september', 'october', 'november', 'december']
        
        # Define seasonal patterns for different climate types
        climate_patterns = {
            "Tropical": {
                "winter": {"temp": 25, "desc": "Warm tropical"},
                "summer": {"temp": 30, "desc": "Hot tropical"},
                "monsoon": {"temp": 28, "desc": "Humid tropical"}
            },
            "Desert": {
                "winter": {"temp": 15, "desc": "Cool desert"},
                "summer": {"temp": 35, "desc": "Very hot desert"},
                "spring": {"temp": 25, "desc": "Warm desert"}
            },
            "Temperate": {
                "winter": {"temp": 5, "desc": "Cold temperate"},
                "summer": {"temp": 22, "desc": "Warm temperate"},
                "spring": {"temp": 15, "desc": "Mild temperate"},
                "autumn": {"temp": 12, "desc": "Cool temperate"}
            },
            "Continental": {
                "winter": {"temp": -5, "desc": "Very cold continental"},
                "summer": {"temp": 20, "desc": "Warm continental"},
                "spring": {"temp": 10, "desc": "Cool continental"}
            }
        }
        
        if climate_type not in climate_patterns:
            return
            
        patterns = climate_patterns[climate_type]
        
        # Assign seasonal data based on month
        for month in months:
            month_num = months.index(month) + 1
            
            if climate_type == "Tropical":
                if month_num in [12, 1, 2]:  # Winter
                    pattern = patterns["winter"]
                elif month_num in [6, 7, 8, 9]:  # Monsoon/Summer
                    pattern = patterns["monsoon"]
                else:  # Other months
                    pattern = patterns["summer"]
                    
            elif climate_type == "Desert":
                if month_num in [12, 1, 2]:  # Winter
                    pattern = patterns["winter"]
                elif month_num in [3, 4, 5]:  # Spring
                    pattern = patterns["spring"]
                else:  # Summer
                    pattern = patterns["summer"]
                    
            elif climate_type == "Temperate":
                if month_num in [12, 1, 2]:  # Winter
                    pattern = patterns["winter"]
                elif month_num in [3, 4, 5]:  # Spring
                    pattern = patterns["spring"]
                elif month_num in [6, 7, 8]:  # Summer
                    pattern = patterns["summer"]
                else:  # Autumn
                    pattern = patterns["autumn"]
                    
            elif climate_type == "Continental":
                if month_num in [12, 1, 2]:  # Winter
                    pattern = patterns["winter"]
                elif month_num in [6, 7, 8]:  # Summer
                    pattern = patterns["summer"]
                else:  # Spring/Autumn
                    pattern = patterns["spring"]
            
            temp_range = f"{pattern['temp']-5}-{pattern['temp']+5}°C"
            
            climate_data["seasonal_weather"][month] = {
                "temp_range": temp_range,
                "description": pattern["desc"],
                "clothing": self._get_clothing_recommendation(pattern["temp"])
            }
    
    def _get_climate_data_from_weather_api(self, city: str, country: str, month: str = None) -> Optional[Dict[str, Any]]:
        """Fallback to free weather API for climate data"""
        try:
            # Use a free weather API that doesn't require authentication
            # We'll use wttr.in which provides weather data without API keys
            
            # Clean city name for URL
            city_clean = city.replace(" ", "+")
            url = f"https://wttr.in/{city_clean}?format=j1"
            
            response = requests.get(url, headers={'User-Agent': 'TravelChatbot/1.0'}, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse weather data
            climate_data = {
                "name": city.title(),
                "region": f"{city.title()}, {country.title()}",
                "climate_type": "Unknown",
                "seasonal_weather": {},
                "source": "WeatherAPI"
            }
            
            # Extract current weather as base
            current_condition = data.get("current_condition", [{}])[0]
            current_temp = current_condition.get("temp_C", "20")
            
            # Create basic seasonal data based on current temperature
            # This is a simplified approach - in production you'd want historical data
            base_temp = int(current_temp) if current_temp.isdigit() else 20
            
            # Adjust temperatures based on hemisphere and month
            months = ['january', 'february', 'march', 'april', 'may', 'june', 
                     'july', 'august', 'september', 'october', 'november', 'december']
            
            for month_name in months:
                month_num = months.index(month_name) + 1
                
                # Simple seasonal adjustment (northern hemisphere bias)
                if month_num in [12, 1, 2]:  # Winter
                    temp_adjust = -10
                elif month_num in [3, 4, 5]:  # Spring
                    temp_adjust = -5
                elif month_num in [6, 7, 8]:  # Summer
                    temp_adjust = 5
                else:  # Autumn
                    temp_adjust = 0
                
                adjusted_temp = base_temp + temp_adjust
                temp_range = f"{adjusted_temp-5}-{adjusted_temp+5}°C"
                
                climate_data["seasonal_weather"][month_name] = {
                    "temp_range": temp_range,
                    "description": self._get_climate_description(adjusted_temp),
                    "clothing": self._get_clothing_recommendation(adjusted_temp)
                }
            
            # Add current month data if requested
            if month and month.lower() in climate_data["seasonal_weather"]:
                climate_data["current_month_weather"] = climate_data["seasonal_weather"][month.lower()]
            
            self.logger.info(f"Successfully retrieved climate data from weather API for {city}")
            return climate_data
            
        except Exception as e:
            self.logger.error(f"Error fetching climate data from weather API: {e}")
            return None
        
    def apply_mcp_filters(self, content: Dict[str, Any], destination: str, month: str = None) -> Dict[str, Any]:
        """Apply MCP filters to ensure culturally sensitive content, enhanced with Wikipedia data"""
        
        filtered_content = content.copy()
        
        # Get fresh cultural data including Wikipedia data
        cultural_data = self.get_cultural_data(destination, month)
        
        # Apply sensitivity checks with enhanced data
        filtered_content = self._apply_sensitivity_filters(filtered_content, destination, cultural_data)
        
        # Add cultural warnings based on festivals and norms
        filtered_content = self._add_cultural_warnings(filtered_content, destination, cultural_data)
        
        # Enhance with respectful alternatives
        filtered_content = self._add_respectful_alternatives(filtered_content, destination, cultural_data)
        
        # Add festival-specific guidance
        if month and cultural_data.get("festivals"):
            filtered_content = self._add_festival_guidance(filtered_content, cultural_data["festivals"])
        
        self.logger.info(f"Applied enhanced MCP filters for {destination}")
        return filtered_content
    
    def filter_product_recommendations(self, products: List[Dict], destination: str, 
                                     cultural_context: Dict, month: str = None) -> List[Dict]:
        """Filter product recommendations based on cultural appropriateness with enhanced data"""
        
        filtered_products = []
        destination_data = self.get_cultural_data(destination, month)
        taboos = destination_data.get("taboos", [])
        
        # Add festival-specific taboos if available
        festivals = destination_data.get("festivals", [])
        for festival in festivals:
            if "taboo" in festival.get("significance", "").lower():
                taboos.append(festival["significance"])
        
        for product in products:
            product_name = product.get("name", "").lower()
            product_description = product.get("description", "").lower()
            categories = [cat.lower() for cat in product.get("categories", [])]
            
            # Check against cultural taboos
            is_appropriate = True
            
            for taboo in taboos:
                taboo_lower = taboo.lower()
                if (taboo_lower in product_name or 
                    taboo_lower in product_description or
                    any(taboo_lower in cat for cat in categories)):
                    is_appropriate = False
                    self.logger.info(f"Filtered product {product_name} due to taboo: {taboo}")
                    break
            
            if is_appropriate:
                # Add cultural appropriateness score
                product_copy = product.copy()
                product_copy["cultural_score"] = self._calculate_cultural_score(
                    product, destination_data
                )
                filtered_products.append(product_copy)
        
        # Sort by cultural appropriateness
        filtered_products.sort(key=lambda x: x.get("cultural_score", 0), reverse=True)
        
        return filtered_products
    
    def _normalize_destination(self, destination: str) -> str:
        """Normalize destination names"""
        destination_mapping = {
            "istanbul": "Turkey",
            "ankara": "Turkey", 
            "uae": "Dubai",
            "emirates": "Dubai",
            "tokyo": "Japan",
            "kyoto": "Japan",
            "karachi": "Pakistan", 
            "lahore": "Pakistan",
            "mumbai": "India",
            "delhi": "India",
            "new delhi": "India"
        }
        
        destination_lower = destination.lower()
        return destination_mapping.get(destination_lower, destination)
    
    def _apply_sensitivity_filters(self, content: Dict, destination: str, cultural_data: Dict = None) -> Dict:
        """Apply sensitivity filters to content with enhanced cultural data"""
        
        if cultural_data is None:
            cultural_data = self.get_cultural_data(destination)
        
        # Check for potentially sensitive content
        if "clothing_norms" in content:
            norms = content["clothing_norms"]
            
            # Ensure respectful language
            for key, value in norms.items():
                if isinstance(value, str):
                    # Replace potentially judgmental language
                    value = value.replace("must", "recommended to")
                    value = value.replace("required", "advised")
                    norms[key] = value
        
        # Add taboos from cultural data
        if cultural_data.get("taboos"):
            content["cultural_taboos"] = cultural_data["taboos"]
        
        return content
    
    def _add_cultural_warnings(self, content: Dict, destination: str, cultural_data: Dict = None) -> Dict:
        """Add cultural sensitivity warnings where appropriate"""
        
        if cultural_data is None:
            cultural_data = self.get_cultural_data(destination)
        
        if destination in ["Dubai", "Pakistan", "Turkey"] or any(country in destination for country in ["Dubai", "Pakistan", "Turkey"]):
            if "sensitivity_flags" not in content:
                content["sensitivity_flags"] = []
            
            content["sensitivity_flags"].append(
                "Please respect local customs and Islamic traditions"
            )
        
        # Add warnings based on taboos
        if cultural_data.get("taboos"):
            if "sensitivity_flags" not in content:
                content["sensitivity_flags"] = []
            
            for taboo in cultural_data["taboos"][:2]:  # Limit to 2 warnings
                content["sensitivity_flags"].append(f"Avoid: {taboo[:50]}...")
        
        return content
    
    def _add_respectful_alternatives(self, content: Dict, destination: str, cultural_data: Dict = None) -> Dict:
        """Add respectful alternatives and suggestions"""
        
        if cultural_data is None:
            cultural_data = self.get_cultural_data(destination)
        
        if "shopping_etiquette" in content:
            if "respectful_shopping" not in content["shopping_etiquette"]:
                content["shopping_etiquette"]["respectful_shopping"] = [
                    "Learn basic local greetings",
                    "Respect local payment customs",
                    "Ask before photographing in markets"
                ]
        
        # Add clothing-specific alternatives based on cultural norms
        if cultural_data.get("clothing_norms"):
            if "clothing_alternatives" not in content:
                content["clothing_alternatives"] = []
            
            norms = cultural_data["clothing_norms"]
            if norms.get("religious_sites"):
                content["clothing_alternatives"].append("Modest clothing options available for religious sites")
            if norms.get("business"):
                content["clothing_alternatives"].append("Formal attire suitable for business settings")
        
        return content
    
    def _add_festival_guidance(self, content: Dict, festivals: List[Dict]) -> Dict:
        """Add festival-specific guidance to content"""
        
        if "festival_guidance" not in content:
            content["festival_guidance"] = []
        
        for festival in festivals[:3]:  # Limit to 3 festivals
            guidance = {
                "festival": festival.get("name", "Local Festival"),
                "significance": festival.get("significance", "Cultural celebration")[:100],
                "clothing_suggestions": festival.get("shopping_relevance", "Traditional attire recommended")
            }
            content["festival_guidance"].append(guidance)
        
        return content
    
    def _calculate_cultural_score(self, product: Dict, destination_data: Dict) -> float:
        """Calculate cultural appropriateness score for a product"""
        
        score = 0.5  # Base score
        
        product_name = product.get("name", "").lower()
        categories = [cat.lower() for cat in product.get("categories", [])]
        
        # Positive scoring for appropriate items
        if any(cat in ["accessories", "clothing"] for cat in categories):
            score += 0.2
        
        # Cultural relevance bonus
        if destination_data.get("gift_culture"):
            gift_culture = destination_data["gift_culture"].lower()
            if "jewelry" in gift_culture and "jewelry" in categories:
                score += 0.3
            if "traditional" in gift_culture and "traditional" in product_name:
                score += 0.3
        
        return min(1.0, score)
    
    def get_festival_recommendations(self, destination: str, timeframe: str = None) -> List[Dict]:
        """Get festival-specific product recommendations"""
        
        destination_data = self.get_cultural_data(destination)
        festivals = destination_data.get("festivals", [])
        
        relevant_festivals = []
        
        if timeframe:
            # Filter festivals by timeframe
            timeframe_lower = timeframe.lower()
            for festival in festivals:
                festival_date = festival.get("date", "").lower()
                if (timeframe_lower in festival_date or 
                    any(month in festival_date for month in [timeframe_lower])):
                    relevant_festivals.append(festival)
        else:
            relevant_festivals = festivals
        
        return relevant_festivals
    
    def get_festivals_from_wikipedia(self, country: str, month: str = None) -> List[Dict]:
        """
        Fetch festivals and events for a country from Wikipedia
        """
        try:
            # Search for festivals page
            search_term = f"Festivals in {country}"
            if month:
                search_term = f"{month} festivals in {country}"
            
            # Wikipedia API search
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(search_term)}&format=json"
            response = requests.get(search_url, headers={'User-Agent': 'TravelChatbot/1.0'}, timeout=10)
            response.raise_for_status()
            
            search_results = response.json()
            festivals = []
            
            # Get the top result and fetch its content
            if search_results['query']['search']:
                page_title = search_results['query']['search'][0]['title']
                
                # Fetch page content
                content_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&explaintext=true&titles={quote(page_title)}&format=json"
                content_response = requests.get(content_url, headers={'User-Agent': 'TravelChatbot/1.0'}, timeout=10)
                content_response.raise_for_status()
                
                content_data = content_response.json()
                pages = content_data['query']['pages']
                
                for page_id, page_data in pages.items():
                    if 'extract' in page_data:
                        extract = page_data['extract']
                        # Parse festivals from the extract
                        festivals = self._parse_festivals_from_text(extract, country, month)
                        break
            
            self.logger.info(f"Fetched {len(festivals)} festivals for {country}")
            return festivals
            
        except Exception as e:
            self.logger.error(f"Error fetching festivals from Wikipedia: {e}")
            return []
    
    def get_cultural_norms_from_wikipedia(self, country: str) -> Dict[str, Any]:
        """
        Fetch cultural norms and seasonal information from Wikipedia
        """
        try:
            # Search for culture/clothing/climate pages
            search_terms = [
                f"Culture of {country}",
                f"Clothing in {country}",
                f"Dress code in {country}",
                f"Climate of {country}"
            ]
            
            cultural_info = {
                "clothing_norms": {},
                "etiquette": "",
                "taboos": [],
                "seasonal_weather": {},
                "climate_info": ""
            }
            
            for term in search_terms:
                search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(term)}&format=json"
                response = requests.get(search_url, headers={'User-Agent': 'TravelChatbot/1.0'}, timeout=10)
                response.raise_for_status()
                
                search_results = response.json()
                
                if search_results['query']['search']:
                    page_title = search_results['query']['search'][0]['title']
                    
                    # Fetch page content
                    content_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&explaintext=true&titles={quote(page_title)}&format=json"
                    content_response = requests.get(content_url, headers={'User-Agent': 'TravelChatbot/1.0'}, timeout=10)
                    content_response.raise_for_status()
                    
                    content_data = content_response.json()
                    pages = content_data['query']['pages']
                    
                    for page_id, page_data in pages.items():
                        if 'extract' in page_data:
                            extract = page_data['extract']
                            # Parse cultural and climate info from the extract
                            parsed_info = self._parse_cultural_and_climate_info(extract, term)
                            cultural_info = self._merge_cultural_and_climate_info(cultural_info, parsed_info)
                            break
                
                # Don't search all terms if we found good info
                if cultural_info['clothing_norms'] or cultural_info['climate_info']:
                    break
            
            self.logger.info(f"Fetched cultural and climate norms for {country}")
            return cultural_info
            
        except Exception as e:
            self.logger.error(f"Error fetching cultural norms from Wikipedia: {e}")
            return {
                "clothing_norms": {"general": "Research local customs for appropriate attire"},
                "etiquette": "",
                "taboos": [],
                "seasonal_weather": {},
                "climate_info": ""
            }
    
    def _parse_festivals_from_text(self, text: str, country: str, month: str = None) -> List[Dict]:
        """Parse festival information from Wikipedia text extract"""
        festivals = []
        
        # Simple parsing - look for festival mentions
        lines = text.split('\n')
        current_festival = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for festival names (usually capitalized or with dates)
            if any(keyword in line.lower() for keyword in ['festival', 'celebration', 'holiday', 'day']):
                if current_festival:
                    festivals.append(current_festival)
                
                current_festival = {
                    "name": line.split('.')[0].strip(),
                    "date": month or "Various",
                    "significance": line,
                    "shopping_relevance": "Traditional clothing and local crafts"
                }
            elif current_festival and len(line) > 20:
                # Add more details to current festival
                current_festival["significance"] += f" {line}"
        
        if current_festival:
            festivals.append(current_festival)
        
        return festivals[:5]  # Limit to 5 festivals
    
    def _parse_cultural_and_climate_info(self, text: str, search_term: str) -> Dict[str, Any]:
        """Parse cultural and climate information from Wikipedia text extract"""
        info = {
            "clothing_norms": {},
            "etiquette": "",
            "taboos": [],
            "seasonal_weather": {},
            "climate_info": ""
        }
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for clothing-related information
            if 'clothing' in search_term.lower():
                if 'dress' in line.lower() or 'wear' in line.lower() or 'attire' in line.lower():
                    if 'religious' in line.lower() or 'mosque' in line.lower():
                        info["clothing_norms"]["religious_sites"] = line
                    elif 'business' in line.lower():
                        info["clothing_norms"]["business"] = line
                    else:
                        info["clothing_norms"]["general"] = line
            
            # Look for climate/seasonal information
            elif 'climate' in search_term.lower():
                # Extract seasonal weather patterns
                if any(season in line.lower() for season in ['summer', 'winter', 'spring', 'autumn', 'fall']):
                    if 'summer' in line.lower():
                        info["seasonal_weather"]["summer"] = line
                    elif 'winter' in line.lower():
                        info["seasonal_weather"]["winter"] = line
                    elif 'spring' in line.lower():
                        info["seasonal_weather"]["spring"] = line
                    elif 'autumn' in line.lower() or 'fall' in line.lower():
                        info["seasonal_weather"]["autumn"] = line
                
                # Store general climate information
                if len(line) > 50 and any(word in line.lower() for word in ['temperature', 'climate', 'weather', 'rainfall']):
                    info["climate_info"] += line + " "
            
            # Look for etiquette information
            if 'etiquette' in line.lower() or 'custom' in line.lower():
                info["etiquette"] += line + " "
            
            # Look for taboos
            if 'avoid' in line.lower() or 'taboo' in line.lower() or 'offensive' in line.lower():
                info["taboos"].append(line)
        
        return info
    
    def _merge_cultural_and_climate_info(self, base_info: Dict, new_info: Dict) -> Dict:
        """Merge new cultural and climate information with existing data"""
        merged = base_info.copy()
        
        # Merge clothing norms
        for key, value in new_info.get("clothing_norms", {}).items():
            if key not in merged["clothing_norms"] or not merged["clothing_norms"][key]:
                merged["clothing_norms"][key] = value
        
        # Merge seasonal weather
        for season, info in new_info.get("seasonal_weather", {}).items():
            if season not in merged["seasonal_weather"]:
                merged["seasonal_weather"][season] = info
        
        # Merge climate info
        if new_info.get("climate_info"):
            merged["climate_info"] += new_info["climate_info"]
        
        # Merge etiquette
        if new_info.get("etiquette"):
            merged["etiquette"] += new_info["etiquette"]
        
        # Merge taboos
        merged["taboos"].extend(new_info.get("taboos", []))
        
        return merged
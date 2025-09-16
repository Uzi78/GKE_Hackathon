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

class CulturalDataManager:
    """
    Manages cultural data and implements MCP filtering for ethical AI responses
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load cultural data
        self.cultural_database = self._load_cultural_database()
        self.mcp_filters = self._load_mcp_filters()
        
        self.logger.info("Cultural Data Manager initialized with MCP filters")
    
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
                "gift_culture": "Hospitality important, traditional crafts valued"
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
    
    def get_cultural_data(self, destination: str) -> Dict[str, Any]:
        """Get cultural data for a destination"""
        
        # Normalize destination name
        destination = self._normalize_destination(destination)
        
        if destination in self.cultural_database:
            data = self.cultural_database[destination].copy()
            
            # Add current seasonal info if available
            current_month = datetime.now().strftime("%B").lower()
            if "seasonal_info" in data and current_month in data["seasonal_info"]:
                data["current_season"] = data["seasonal_info"][current_month]
            
            self.logger.info(f"Retrieved cultural data for {destination}")
            return data
        else:
            # Fallback for unknown destinations
            return {
                "clothing_norms": {
                    "general": "Respectful, modest dress recommended",
                    "religious_sites": "Conservative clothing advised",
                    "business": "Formal attire appropriate",
                    "casual": "Smart casual recommended"
                },
                "festivals": [],
                "taboos": [],
                "gift_culture": "Research local customs for gift-giving",
                "note": f"Limited cultural data available for {destination}"
            }
    
    def apply_mcp_filters(self, content: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Apply MCP filters to ensure culturally sensitive content"""
        
        filtered_content = content.copy()
        
        # Apply sensitivity checks
        filtered_content = self._apply_sensitivity_filters(filtered_content, destination)
        
        # Add cultural warnings if needed
        filtered_content = self._add_cultural_warnings(filtered_content, destination)
        
        # Enhance with respectful alternatives
        filtered_content = self._add_respectful_alternatives(filtered_content, destination)
        
        self.logger.info(f"Applied MCP filters for {destination}")
        return filtered_content
    
    def filter_product_recommendations(self, products: List[Dict], destination: str, 
                                     cultural_context: Dict) -> List[Dict]:
        """Filter product recommendations based on cultural appropriateness"""
        
        filtered_products = []
        destination_data = self.get_cultural_data(destination)
        taboos = destination_data.get("taboos", [])
        
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
    
    def _apply_sensitivity_filters(self, content: Dict, destination: str) -> Dict:
        """Apply sensitivity filters to content"""
        
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
        
        return content
    
    def _add_cultural_warnings(self, content: Dict, destination: str) -> Dict:
        """Add cultural sensitivity warnings where appropriate"""
        
        if destination in ["Dubai", "Pakistan"]:
            if "sensitivity_flags" not in content:
                content["sensitivity_flags"] = []
            
            content["sensitivity_flags"].append(
                "Please respect local customs and Islamic traditions"
            )
        
        return content
    
    def _add_respectful_alternatives(self, content: Dict, destination: str) -> Dict:
        """Add respectful alternatives and suggestions"""
        
        if "shopping_etiquette" in content:
            if "respectful_shopping" not in content["shopping_etiquette"]:
                content["shopping_etiquette"]["respectful_shopping"] = [
                    "Learn basic local greetings",
                    "Respect local payment customs",
                    "Ask before photographing in markets"
                ]
        
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
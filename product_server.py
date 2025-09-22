#!/usr/bin/env python3
"""
Enhanced Product Catalog Server for Travel Chatbot Testing
Includes diverse products across all categories with proper cultural considerations
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import random
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Comprehensive product catalog for rigorous testing
ENHANCED_PRODUCT_CATALOG = [
    # CLOTHING - Winter/Cold Weather
    {
        'id': 'CLT_WJKT_001',
        'name': 'Heavy Winter Parka',
        'description': 'Arctic-grade insulated parka with fur-lined hood, waterproof and windproof. Perfect for extreme cold climates.',
        'picture': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 249, 'nanos': 990000000},
        'categories': ['clothing', 'outerwear', 'winter', 'cold', 'extreme-weather', 'unisex']
    },
    {
        'id': 'CLT_WOOL_002',
        'name': 'Merino Wool Thermal Set',
        'description': 'Premium base layer thermal underwear set. Moisture-wicking and odor-resistant.',
        'picture': 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 89, 'nanos': 990000000},
        'categories': ['clothing', 'underwear', 'thermal', 'cold', 'winter', 'unisex', 'hiking']
    },
    {
        'id': 'CLT_DOWN_003',
        'name': 'Down Jacket',
        'description': 'Lightweight packable down jacket. Compressible and perfect for layering.',
        'picture': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5e?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 179, 'nanos': 990000000},
        'categories': ['clothing', 'outerwear', 'winter', 'mild', 'travel', 'packable', 'unisex']
    },
    
    # CLOTHING - Summer/Hot Weather
    {
        'id': 'CLT_LINEN_004',
        'name': 'Linen Shirt',
        'description': 'Breathable long-sleeve linen shirt. Perfect for hot climates while maintaining coverage.',
        'picture': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 69, 'nanos': 990000000},
        'categories': ['clothing', 'shirts', 'summer', 'hot', 'breathable', 'modest', 'business-casual', 'unisex']
    },
    {
        'id': 'CLT_SUN_005',
        'name': 'UV Protection Rashguard',
        'description': 'Long-sleeve rashguard with UPF 50+ sun protection. Suitable for conservative beach destinations.',
        'picture': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 45, 'nanos': 990000000},
        'categories': ['clothing', 'swimwear', 'summer', 'hot', 'modest', 'beach', 'sun-protection', 'unisex']
    },
    {
        'id': 'CLT_COTTON_006',
        'name': 'Organic Cotton T-Shirt',
        'description': 'Soft, breathable organic cotton t-shirt. Classic fit suitable for all occasions.',
        'picture': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 29, 'nanos': 990000000},
        'categories': ['clothing', 'casual', 'summer', 'hot', 'mild', 'breathable', 'unisex', 'sustainable']
    },
    
    # CLOTHING - Traditional & Cultural
    {
        'id': 'CLT_TRAD_007',
        'name': 'Embroidered Kurta',
        'description': 'Traditional Pakistani/Indian kurta with intricate embroidery. Perfect for cultural events.',
        'picture': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 89, 'nanos': 990000000},
        'categories': ['clothing', 'traditional', 'cultural', 'formal', 'pakistan', 'india', 'festival', 'unisex']
    },
    {
        'id': 'CLT_KIMONO_008',
        'name': 'Casual Kimono',
        'description': 'Lightweight kimono-style jacket. Respectful modern interpretation of traditional Japanese wear.',
        'picture': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 125, 'nanos': 990000000},
        'categories': ['clothing', 'traditional', 'cultural', 'japan', 'casual', 'layering', 'respectful']
    },
    {
        'id': 'CLT_ABAYA_009',
        'name': 'Modern Abaya',
        'description': 'Contemporary abaya with subtle embellishments. Elegant modest wear for formal occasions.',
        'picture': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 159, 'nanos': 990000000},
        'categories': ['clothing', 'traditional', 'modest', 'formal', 'middle-east', 'dubai', 'conservative', 'women']
    },
    
    # CLOTHING - Business & Formal
    {
        'id': 'CLT_SUIT_010',
        'name': 'Business Suit',
        'description': 'Professional wool blend suit. Perfect for international business meetings.',
        'picture': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 399, 'nanos': 990000000},
        'categories': ['clothing', 'formal', 'business', 'professional', 'suit', 'conservative', 'unisex']
    },
    {
        'id': 'CLT_BLOUSE_011',
        'name': 'Conservative Blouse',
        'description': 'Long-sleeve blouse with modest neckline. Suitable for conservative business environments.',
        'picture': 'https://images.unsplash.com/photo-1564257577154-75b5a3f75364?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 79, 'nanos': 990000000},
        'categories': ['clothing', 'business', 'formal', 'modest', 'conservative', 'professional', 'women']
    },
    
    # ACCESSORIES - Head Coverings & Cultural
    {
        'id': 'ACC_SCARF_012',
        'name': 'Silk Headscarf',
        'description': 'Elegant silk scarf suitable for religious sites and cultural respect.',
        'picture': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 49, 'nanos': 990000000},
        'categories': ['accessories', 'headwear', 'modest', 'religious', 'silk', 'respectful', 'cultural', 'women']
    },
    {
        'id': 'ACC_HAT_013',
        'name': 'Wide-Brim Sun Hat',
        'description': 'Stylish sun hat with UPF protection. Essential for desert and tropical climates.',
        'picture': 'https://images.unsplash.com/photo-1521369909029-2afed882baee?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 35, 'nanos': 990000000},
        'categories': ['accessories', 'headwear', 'sun-protection', 'summer', 'hot', 'desert', 'tropical', 'unisex']
    },
    {
        'id': 'ACC_BEANIE_014',
        'name': 'Wool Beanie',
        'description': 'Warm knitted beanie for cold weather destinations.',
        'picture': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 25, 'nanos': 990000000},
        'categories': ['accessories', 'headwear', 'winter', 'cold', 'warm', 'unisex']
    },
    
    # ACCESSORIES - Religious & Cultural Items
    {
        'id': 'ACC_PRAYER_015',
        'name': 'Travel Prayer Mat',
        'description': 'Compact, portable prayer mat with built-in compass. Respectful travel essential.',
        'picture': 'https://images.unsplash.com/photo-1609198092458-38a293c7ac4b?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 39, 'nanos': 990000000},
        'categories': ['accessories', 'religious', 'islamic', 'travel', 'spiritual', 'respectful', 'portable']
    },
    {
        'id': 'ACC_MALA_016',
        'name': 'Meditation Mala Beads',
        'description': 'Traditional 108-bead mala for meditation and spiritual practice.',
        'picture': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5e?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 29, 'nanos': 990000000},
        'categories': ['accessories', 'religious', 'spiritual', 'meditation', 'buddhist', 'hindu', 'cultural']
    },
    
    # FOOTWEAR - Climate Specific
    {
        'id': 'FOOT_BOOTS_017',
        'name': 'Waterproof Hiking Boots',
        'description': 'Durable waterproof boots with ankle support. Perfect for mountain regions.',
        'picture': 'https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 189, 'nanos': 990000000},
        'categories': ['footwear', 'hiking', 'waterproof', 'cold', 'mountains', 'outdoor', 'durable', 'unisex']
    },
    {
        'id': 'FOOT_SANDALS_018',
        'name': 'Modest Walking Sandals',
        'description': 'Comfortable closed-toe sandals suitable for conservative destinations.',
        'picture': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 69, 'nanos': 990000000},
        'categories': ['footwear', 'sandals', 'summer', 'hot', 'modest', 'walking', 'conservative', 'unisex']
    },
    {
        'id': 'FOOT_SLIP_019',
        'name': 'Easy-Remove Slip-on Shoes',
        'description': 'Convenient slip-on shoes perfect for cultures where shoes are removed frequently.',
        'picture': 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 89, 'nanos': 990000000},
        'categories': ['footwear', 'slip-on', 'convenient', 'cultural', 'respectful', 'asia', 'temples', 'unisex']
    },
    
    # SWIMWEAR - Culturally Appropriate
    {
        'id': 'SWIM_BURKINI_020',
        'name': 'Full-Coverage Burkini',
        'description': 'Modest full-body swimsuit with hijab. Perfect for conservative beach destinations.',
        'picture': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 119, 'nanos': 990000000},
        'categories': ['swimwear', 'modest', 'conservative', 'islamic', 'beach', 'full-coverage', 'women']
    },
    {
        'id': 'SWIM_RASH_021',
        'name': 'Long-Sleeve Swim Shirt',
        'description': 'Modest swim shirt with UPF 50+ protection. Suitable for conservative beach areas.',
        'picture': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 55, 'nanos': 990000000},
        'categories': ['swimwear', 'modest', 'sun-protection', 'beach', 'conservative', 'unisex']
    },
    {
        'id': 'SWIM_COVER_022',
        'name': 'Beach Cover-up Kaftan',
        'description': 'Flowing beach kaftan for modest coverage. Stylish and respectful.',
        'picture': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 65, 'nanos': 990000000},
        'categories': ['swimwear', 'cover-up', 'modest', 'beach', 'kaftan', 'flowing', 'women']
    },
    
    # GIFTS - Cultural & Regional
    {
        'id': 'GIFT_TEA_023',
        'name': 'Premium Tea Gift Set',
        'description': 'Curated selection of regional teas with beautiful packaging. Perfect cultural gift.',
        'picture': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 45, 'nanos': 990000000},
        'categories': ['gifts', 'tea', 'cultural', 'edible', 'premium', 'traditional', 'hospitality']
    },
    {
        'id': 'GIFT_CRAFT_024',
        'name': 'Handcrafted Wooden Box',
        'description': 'Beautifully carved wooden jewelry box. Represents local craftsmanship.',
        'picture': 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 79, 'nanos': 990000000},
        'categories': ['gifts', 'handicraft', 'wooden', 'cultural', 'artisan', 'traditional', 'decorative']
    },
    {
        'id': 'GIFT_DATES_025',
        'name': 'Premium Date Gift Box',
        'description': 'Luxury Medjool dates in elegant packaging. Traditional Middle Eastern gift.',
        'picture': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 35, 'nanos': 990000000},
        'categories': ['gifts', 'food', 'dates', 'middle-east', 'ramadan', 'eid', 'traditional', 'premium']
    },
    {
        'id': 'GIFT_SILK_026',
        'name': 'Silk Pocket Square Set',
        'description': 'Set of traditional silk pocket squares. Elegant and culturally appropriate.',
        'picture': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 89, 'nanos': 990000000},
        'categories': ['gifts', 'accessories', 'silk', 'formal', 'traditional', 'elegant', 'business']
    },
    
    # ELECTRONICS - Travel Specific
    {
        'id': 'ELEC_ADAPTER_027',
        'name': 'Universal Travel Adapter',
        'description': 'All-in-one adapter with USB charging ports. Compatible with 150+ countries.',
        'picture': 'https://images.unsplash.com/photo-1609198092458-38a293c7ac4b?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 49, 'nanos': 990000000},
        'categories': ['electronics', 'travel', 'adapter', 'universal', 'charging', 'essential', 'portable']
    },
    {
        'id': 'ELEC_CAMERA_028',
        'name': 'Compact Travel Camera',
        'description': 'Lightweight camera with excellent low-light performance. Perfect for cultural sites.',
        'picture': 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 299, 'nanos': 990000000},
        'categories': ['electronics', 'camera', 'travel', 'photography', 'compact', 'cultural-sites']
    },
    {
        'id': 'ELEC_BANK_029',
        'name': 'Solar Power Bank',
        'description': 'Eco-friendly solar power bank. Essential for desert and remote destinations.',
        'picture': 'https://images.unsplash.com/photo-1609198092458-38a293c7ac4b?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 79, 'nanos': 990000000},
        'categories': ['electronics', 'power-bank', 'solar', 'eco-friendly', 'desert', 'remote', 'sustainable']
    },
    
    # BEAUTY & PERSONAL CARE - Climate Adapted
    {
        'id': 'BEAUTY_SUN_030',
        'name': 'High SPF Sunscreen Set',
        'description': 'SPF 50+ sunscreen for face and body. Essential for tropical and desert climates.',
        'picture': 'https://images.unsplash.com/photo-1556228724-c2eab21e32ef?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 35, 'nanos': 990000000},
        'categories': ['beauty', 'sunscreen', 'sun-protection', 'tropical', 'desert', 'hot', 'essential']
    },
    {
        'id': 'BEAUTY_BALM_031',
        'name': 'Cold Weather Lip Balm',
        'description': 'Heavy-duty lip balm with SPF. Protection against cold, wind, and high altitude.',
        'picture': 'https://images.unsplash.com/photo-1556228724-c2eab21e32ef?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 15, 'nanos': 990000000},
        'categories': ['beauty', 'lip-balm', 'cold', 'winter', 'protection', 'mountain', 'essential']
    },
    {
        'id': 'BEAUTY_MIST_032',
        'name': 'Cooling Face Mist',
        'description': 'Refreshing face mist with aloe vera. Perfect for hot, humid climates.',
        'picture': 'https://images.unsplash.com/photo-1556228724-c2eab21e32ef?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 25, 'nanos': 990000000},
        'categories': ['beauty', 'face-mist', 'cooling', 'hot', 'humid', 'refreshing', 'travel-size']
    },
    
    # HOME & DECOR - Cultural Items
    {
        'id': 'HOME_LAMP_033',
        'name': 'Moroccan Style Lantern',
        'description': 'Ornate metal lantern inspired by Middle Eastern design. Beautiful cultural decor.',
        'picture': 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 89, 'nanos': 990000000},
        'categories': ['home', 'decor', 'lantern', 'moroccan', 'middle-east', 'cultural', 'ornate']
    },
    {
        'id': 'HOME_RUG_034',
        'name': 'Traditional Kilim Rug',
        'description': 'Handwoven kilim rug with traditional patterns. Authentic cultural home decor.',
        'picture': 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 199, 'nanos': 990000000},
        'categories': ['home', 'decor', 'rug', 'kilim', 'handwoven', 'traditional', 'cultural', 'authentic']
    },
    {
        'id': 'HOME_INCENSE_035',
        'name': 'Sandalwood Incense Set',
        'description': 'Premium sandalwood incense with holder. Perfect for meditation and cultural practices.',
        'picture': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 29, 'nanos': 990000000},
        'categories': ['home', 'incense', 'sandalwood', 'meditation', 'spiritual', 'cultural', 'aromatherapy']
    },
    
    # BAGS & LUGGAGE - Travel Specific
    {
        'id': 'BAG_PACK_036',
        'name': 'Anti-Theft Travel Backpack',
        'description': 'Security backpack with RFID blocking and hidden zippers. Perfect for crowded markets.',
        'picture': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 129, 'nanos': 990000000},
        'categories': ['bags', 'backpack', 'travel', 'security', 'anti-theft', 'markets', 'urban']
    },
    {
        'id': 'BAG_MODEST_037',
        'name': 'Modest Shoulder Bag',
        'description': 'Conservative crossbody bag that maintains cultural appropriateness.',
        'picture': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 69, 'nanos': 990000000},
        'categories': ['bags', 'shoulder-bag', 'crossbody', 'modest', 'conservative', 'cultural', 'women']
    },
    
    # OUTDOORS & SPORTS - Activity Specific
    {
        'id': 'OUTDOOR_TENT_038',
        'name': 'Desert Camping Tent',
        'description': '4-season tent designed for desert conditions. UV resistant and sand-proof.',
        'picture': 'https://images.unsplash.com/photo-1504851149312-7a075b496cc7?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 349, 'nanos': 990000000},
        'categories': ['outdoor', 'camping', 'tent', 'desert', '4-season', 'uv-resistant', 'adventure']
    },
    {
        'id': 'OUTDOOR_YOGA_039',
        'name': 'Travel Yoga Mat',
        'description': 'Foldable yoga mat perfect for hotel rooms and cultural mindfulness practices.',
        'picture': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5e?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 45, 'nanos': 990000000},
        'categories': ['outdoor', 'yoga', 'fitness', 'travel', 'foldable', 'mindfulness', 'wellness']
    },
    
    # BOOKS & CULTURE - Educational
    {
        'id': 'BOOK_GUIDE_040',
        'name': 'Cultural Etiquette Guidebook',
        'description': 'Comprehensive guide to cultural customs and etiquette across different countries.',
        'picture': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 25, 'nanos': 990000000},
        'categories': ['books', 'cultural', 'etiquette', 'education', 'travel', 'reference', 'respectful']
    },
    {
        'id': 'BOOK_PHRASE_041',
        'name': 'Multi-Language Phrase Book',
        'description': 'Essential phrases in 12 languages with cultural context and pronunciation.',
        'picture': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 19, 'nanos': 990000000},
        'categories': ['books', 'language', 'phrases', 'multi-language', 'cultural', 'communication']
    },
    
    # PROBLEMATIC ITEMS FOR TESTING (should be filtered by cultural filters)
    {
        'id': 'PROB_BIKINI_042',
        'name': 'String Bikini',
        'description': 'Minimal coverage bikini swimsuit.',
        'picture': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 45, 'nanos': 990000000},
        'categories': ['swimwear', 'bikini', 'revealing', 'beach', 'minimal', 'inappropriate-conservative']
    },
    {
        'id': 'PROB_CROP_043',
        'name': 'Crop Top',
        'description': 'Ultra-short crop top exposing midriff.',
        'picture': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 25, 'nanos': 990000000},
        'categories': ['clothing', 'tops', 'crop', 'revealing', 'midriff', 'inappropriate-conservative']
    },
    {
        'id': 'PROB_ALCOHOL_044',
        'name': 'Wine Gift Set',
        'description': 'Premium wine collection for gifting.',
        'picture': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 89, 'nanos': 990000000},
        'categories': ['gifts', 'alcohol', 'wine', 'inappropriate-islamic', 'inappropriate-conservative']
    },
    {
        'id': 'PROB_SHORTS_045',
        'name': 'Hot Pants Shorts',
        'description': 'Very short shorts with minimal coverage.',
        'picture': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=300&h=300&fit=crop&crop=center',
        'priceUsd': {'currency_code': 'USD', 'units': 35, 'nanos': 990000000},
        'categories': ['clothing', 'shorts', 'revealing', 'minimal', 'hot-pants', 'inappropriate-conservative']
    }
]

# Add price_usd for backward compatibility
for product in ENHANCED_PRODUCT_CATALOG:
    if 'price_usd' not in product and 'priceUsd' in product:
        product['price_usd'] = product['priceUsd']

@app.route('/')
def home():
    """Root endpoint with comprehensive API documentation"""
    categories = set()
    for product in ENHANCED_PRODUCT_CATALOG:
        categories.update(product.get('categories', []))
    
    return jsonify({
        "service": "Enhanced Product Catalog API for Travel Chatbot Testing",
        "version": "2.0.0",
        "description": "Comprehensive product catalog with cultural considerations for rigorous chatbot testing",
        "endpoints": {
            "/": "GET - This documentation",
            "/products": "GET - List all products (supports filtering)",
            "/products/<product_id>": "GET - Get specific product by ID",
            "/categories": "GET - List all available categories",
            "/health": "GET - Health check",
            "/stats": "GET - Catalog statistics",
            "/test/cultural-filter": "GET - Test cultural filtering",
            "/test/climate-filter": "GET - Test climate-based filtering"
        },
        "filters": {
            "category": "Filter by category (case-insensitive)",
            "search": "Search in name and description",
            "price_min": "Minimum price in USD",
            "price_max": "Maximum price in USD",
            "exclude_inappropriate": "Exclude culturally inappropriate items",
            "climate": "Filter by climate (hot/cold/mild/tropical/desert)",
            "cultural": "Filter by cultural appropriateness (conservative/modest/traditional)",
            "limit": "Maximum number of results"
        },
        "total_products": len(ENHANCED_PRODUCT_CATALOG),
        "categories_available": sorted(list(categories))
    })

@app.route('/health')
def health_check():
    """Enhanced health check with catalog statistics"""
    categories = {}
    for product in ENHANCED_PRODUCT_CATALOG:
        for cat in product.get('categories', []):
            categories[cat] = categories.get(cat, 0) + 1
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "catalog": {
            "total_products": len(ENHANCED_PRODUCT_CATALOG),
            "categories_count": len(categories),
            "top_categories": sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]
        },
        "test_ready": True
    })

@app.route('/stats')
def get_stats():
    """Detailed catalog statistics for testing insights"""
    stats = {
        "total_products": len(ENHANCED_PRODUCT_CATALOG),
        "categories": {},
        "price_ranges": {"under_50": 0, "50_100": 0, "100_200": 0, "over_200": 0},
        "cultural_categories": {
            "modest": 0,
            "traditional": 0,
            "conservative": 0,
            "inappropriate": 0
        },
        "climate_categories": {
            "hot": 0,
            "cold": 0,
            "mild": 0,
            "all-weather": 0
        }
    }
    
    for product in ENHANCED_PRODUCT_CATALOG:
        # Category stats
        for cat in product.get('categories', []):
            stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
        
        # Price stats
        price = product.get('priceUsd', {}).get('units', 0)
        if price < 50:
            stats["price_ranges"]["under_50"] += 1
        elif price < 100:
            stats["price_ranges"]["50_100"] += 1
        elif price < 200:
            stats["price_ranges"]["100_200"] += 1
        else:
            stats["price_ranges"]["over_200"] += 1
        
        # Cultural appropriateness
        categories = product.get('categories', [])
        if any('modest' in cat or 'conservative' in cat for cat in categories):
            stats["cultural_categories"]["modest"] += 1
        if any('traditional' in cat for cat in categories):
            stats["cultural_categories"]["traditional"] += 1
        if any('inappropriate' in cat for cat in categories):
            stats["cultural_categories"]["inappropriate"] += 1
        
        # Climate categories
        if any('hot' in cat or 'summer' in cat or 'tropical' in cat for cat in categories):
            stats["climate_categories"]["hot"] += 1
        if any('cold' in cat or 'winter' in cat for cat in categories):
            stats["climate_categories"]["cold"] += 1
        if any('mild' in cat for cat in categories):
            stats["climate_categories"]["mild"] += 1
        if any('all-weather' in cat for cat in categories):
            stats["climate_categories"]["all-weather"] += 1
    
    return jsonify(stats)

@app.route('/products')
def get_products():
    """
    Enhanced product filtering with comprehensive options for testing
    """
    products = ENHANCED_PRODUCT_CATALOG.copy()
    
    # Basic filters
    category = request.args.get('category', '').strip().lower()
    search = request.args.get('search', '').strip().lower()
    climate = request.args.get('climate', '').strip().lower()
    cultural = request.args.get('cultural', '').strip().lower()
    exclude_inappropriate = request.args.get('exclude_inappropriate', '').lower() == 'true'
    
    # Price filters
    try:
        price_min = float(request.args.get('price_min', 0))
        price_max = float(request.args.get('price_max', float('inf')))
    except ValueError:
        price_min, price_max = 0, float('inf')
    
    # Apply category filter
    if category:
        products = [
            p for p in products
            if any(category in cat.lower() for cat in p.get('categories', []))
        ]
    
    # Apply search filter
    if search:
        products = [
            p for p in products
            if (search in p.get('name', '').lower() or 
                search in p.get('description', '').lower() or
                any(search in cat.lower() for cat in p.get('categories', [])))
        ]
    
    # Apply price filter
    products = [
        p for p in products
        if price_min <= p.get('priceUsd', {}).get('units', 0) <= price_max
    ]
    
    # Apply climate filter
    if climate:
        climate_keywords = {
            'hot': ['hot', 'summer', 'tropical', 'desert'],
            'cold': ['cold', 'winter', 'thermal'],
            'mild': ['mild', 'spring', 'autumn'],
            'desert': ['desert', 'sand', 'dry'],
            'tropical': ['tropical', 'humid'],
            'mountain': ['mountain', 'hiking', 'altitude']
        }
        
        if climate in climate_keywords:
            keywords = climate_keywords[climate]
            products = [
                p for p in products
                if any(keyword in cat.lower() for keyword in keywords 
                      for cat in p.get('categories', []))
            ]
    
    # Apply cultural filter
    if cultural:
        cultural_keywords = {
            'conservative': ['conservative', 'modest', 'covered'],
            'modest': ['modest', 'conservative', 'respectful'],
            'traditional': ['traditional', 'cultural', 'authentic'],
            'religious': ['religious', 'spiritual', 'respectful'],
            'business': ['business', 'professional', 'formal']
        }
        
        if cultural in cultural_keywords:
            keywords = cultural_keywords[cultural]
            products = [
                p for p in products
                if any(keyword in cat.lower() for keyword in keywords 
                      for cat in p.get('categories', []))
            ]
    
    # Exclude inappropriate items for conservative destinations
    if exclude_inappropriate:
        products = [
            p for p in products
            if not any('inappropriate' in cat.lower() for cat in p.get('categories', []))
        ]
    
    # Apply limit
    limit = request.args.get('limit')
    if limit:
        try:
            limit = int(limit)
            products = products[:limit]
        except ValueError:
            pass
    
    # Add debug info for testing
    filters_applied = []
    if category: filters_applied.append(f"category:{category}")
    if search: filters_applied.append(f"search:{search}")
    if climate: filters_applied.append(f"climate:{climate}")
    if cultural: filters_applied.append(f"cultural:{cultural}")
    if exclude_inappropriate: filters_applied.append("exclude_inappropriate:true")
    if price_min > 0: filters_applied.append(f"price_min:{price_min}")
    if price_max < float('inf'): filters_applied.append(f"price_max:{price_max}")
    
    logger.info(f"Returning {len(products)} products with filters: {filters_applied}")
    
    response = {
        "products": products,
        "metadata": {
            "total_results": len(products),
            "total_catalog": len(ENHANCED_PRODUCT_CATALOG),
            "filters_applied": filters_applied,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    return jsonify(response.get('products', []) if request.args.get('simple') else response)

@app.route('/products/<product_id>')
def get_product(product_id):
    """Get a specific product by ID with detailed information"""
    product = next((p for p in ENHANCED_PRODUCT_CATALOG if p['id'] == product_id), None)
    
    if product:
        # Add additional metadata for testing
        enhanced_product = product.copy()
        enhanced_product['metadata'] = {
            'cultural_appropriateness': 'appropriate' if not any('inappropriate' in cat for cat in product.get('categories', [])) else 'requires_filtering',
            'climate_suitability': [cat for cat in product.get('categories', []) if cat in ['hot', 'cold', 'mild', 'tropical', 'desert']],
            'target_demographics': [cat for cat in product.get('categories', []) if cat in ['men', 'women', 'unisex', 'children']],
            'fetched_at': datetime.now().isoformat()
        }
        
        logger.info(f"Found product: {product_id}")
        return jsonify(enhanced_product)
    else:
        logger.warning(f"Product not found: {product_id}")
        return jsonify({"error": "Product not found", "product_id": product_id}), 404

@app.route('/categories')
def get_categories():
    """Get all unique categories with counts and descriptions"""
    categories = {}
    category_descriptions = {
        'clothing': 'Apparel and garments for all climates',
        'accessories': 'Supplementary items like bags, jewelry, headwear',
        'footwear': 'Shoes, sandals, boots for different terrains',
        'swimwear': 'Beach and water activity clothing',
        'gifts': 'Items suitable for cultural gifting',
        'electronics': 'Travel-friendly tech devices',
        'beauty': 'Personal care and cosmetic products',
        'home': 'Decorative and functional home items',
        'outdoor': 'Equipment for outdoor activities',
        'books': 'Educational and cultural reading materials',
        'modest': 'Culturally appropriate conservative clothing',
        'traditional': 'Items reflecting local cultural heritage',
        'conservative': 'Suitable for strict dress codes',
        'hot': 'Appropriate for high temperature climates',
        'cold': 'Suitable for low temperature environments',
        'inappropriate-conservative': 'Items that may be filtered for conservative destinations'
    }
    
    for product in ENHANCED_PRODUCT_CATALOG:
        for cat in product.get('categories', []):
            categories[cat] = categories.get(cat, 0) + 1
    
    category_data = []
    for cat, count in sorted(categories.items()):
        category_data.append({
            'name': cat,
            'count': count,
            'description': category_descriptions.get(cat, 'Product category')
        })
    
    return jsonify({
        "categories": category_data,
        "total_categories": len(categories),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/test/cultural-filter')
def test_cultural_filter():
    """Test endpoint to verify cultural filtering works correctly"""
    test_results = {
        "conservative_destinations": {},
        "liberal_destinations": {},
        "inappropriate_items_found": []
    }
    
    # Test conservative filtering
    conservative_products = [
        p for p in ENHANCED_PRODUCT_CATALOG
        if not any('inappropriate' in cat for cat in p.get('categories', []))
    ]
    
    # Test liberal destinations (no filtering)
    liberal_products = ENHANCED_PRODUCT_CATALOG
    
    # Find inappropriate items for testing
    inappropriate_items = [
        p for p in ENHANCED_PRODUCT_CATALOG
        if any('inappropriate' in cat for cat in p.get('categories', []))
    ]
    
    test_results["conservative_destinations"] = {
        "total_products": len(conservative_products),
        "filtered_out": len(ENHANCED_PRODUCT_CATALOG) - len(conservative_products),
        "sample_appropriate": [p['name'] for p in conservative_products[:5]]
    }
    
    test_results["liberal_destinations"] = {
        "total_products": len(liberal_products),
        "sample_products": [p['name'] for p in liberal_products[:5]]
    }
    
    test_results["inappropriate_items_found"] = [
        {"id": p['id'], "name": p['name'], "categories": p['categories']}
        for p in inappropriate_items
    ]
    
    return jsonify(test_results)

@app.route('/test/climate-filter')
def test_climate_filter():
    """Test endpoint to verify climate-based filtering"""
    climate_tests = {}
    
    climates = ['hot', 'cold', 'mild', 'tropical', 'desert']
    
    for climate in climates:
        if climate == 'hot':
            suitable_products = [
                p for p in ENHANCED_PRODUCT_CATALOG
                if any(keyword in cat.lower() for keyword in ['hot', 'summer', 'tropical']
                      for cat in p.get('categories', []))
            ]
        elif climate == 'cold':
            suitable_products = [
                p for p in ENHANCED_PRODUCT_CATALOG
                if any(keyword in cat.lower() for keyword in ['cold', 'winter', 'thermal']
                      for cat in p.get('categories', []))
            ]
        else:
            suitable_products = [
                p for p in ENHANCED_PRODUCT_CATALOG
                if any(climate in cat.lower() for cat in p.get('categories', []))
            ]
        
        climate_tests[climate] = {
            "suitable_products": len(suitable_products),
            "sample_items": [
                {"name": p['name'], "categories": [cat for cat in p['categories'] if climate in cat.lower() or any(kw in cat.lower() for kw in ['hot', 'summer'] if climate == 'hot') or any(kw in cat.lower() for kw in ['cold', 'winter'] if climate == 'cold')]}
                for p in suitable_products[:3]
            ]
        }
    
    return jsonify(climate_tests)

@app.route('/test/random-selection')
def get_random_selection():
    """Get a random selection of products for testing varied scenarios"""
    limit = min(int(request.args.get('limit', 10)), 20)
    
    # Ensure we get a diverse selection
    categories_to_sample = ['clothing', 'accessories', 'gifts', 'modest', 'traditional', 'inappropriate-conservative']
    diverse_products = []
    
    for category in categories_to_sample:
        cat_products = [p for p in ENHANCED_PRODUCT_CATALOG 
                       if any(category in cat.lower() for cat in p.get('categories', []))]
        if cat_products:
            diverse_products.extend(random.sample(cat_products, min(2, len(cat_products))))
    
    # Fill remaining slots with random products
    remaining_slots = limit - len(diverse_products)
    if remaining_slots > 0:
        remaining_products = [p for p in ENHANCED_PRODUCT_CATALOG if p not in diverse_products]
        diverse_products.extend(random.sample(remaining_products, min(remaining_slots, len(remaining_products))))
    
    return jsonify({
        "products": diverse_products[:limit],
        "selection_strategy": "diverse_random",
        "total_selected": len(diverse_products[:limit])
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/", "/products", "/products/<id>", "/categories", "/health", "/stats",
            "/test/cultural-filter", "/test/climate-filter", "/test/random-selection"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "Please check server logs for details",
        "timestamp": datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ENHANCED PRODUCT CATALOG SERVER FOR TRAVEL CHATBOT TESTING")
    print("=" * 60)
    print(f"📊 Total Products: {len(ENHANCED_PRODUCT_CATALOG)}")
    
    # Count categories
    all_categories = set()
    for product in ENHANCED_PRODUCT_CATALOG:
        all_categories.update(product.get('categories', []))
    print(f"🏷️  Categories: {len(all_categories)}")
    
    # Count inappropriate items for testing
    inappropriate_count = len([p for p in ENHANCED_PRODUCT_CATALOG 
                              if any('inappropriate' in cat for cat in p.get('categories', []))])
    print(f"⚠️  Items for Cultural Filter Testing: {inappropriate_count}")
    
    print("\n🌐 Available Endpoints:")
    print("   📋 Documentation: http://localhost:8080")
    print("   🛍️  All Products: http://localhost:8080/products")
    print("   🔍 Search: http://localhost:8080/products?search=modest")
    print("   🏷️  Categories: http://localhost:8080/products?category=clothing")
    print("   🌡️  Climate Filter: http://localhost:8080/products?climate=hot")
    print("   🕌 Cultural Filter: http://localhost:8080/products?cultural=conservative")
    print("   ❌ Exclude Inappropriate: http://localhost:8080/products?exclude_inappropriate=true")
    print("   💰 Price Range: http://localhost:8080/products?price_min=20&price_max=100")
    print("\n🧪 Testing Endpoints:")
    print("   🕌 Cultural Test: http://localhost:8080/test/cultural-filter")
    print("   🌡️  Climate Test: http://localhost:8080/test/climate-filter")
    print("   🎲 Random Selection: http://localhost:8080/test/random-selection")
    print("   📊 Statistics: http://localhost:8080/stats")
    
    print("\n🎯 Perfect for testing these scenarios:")
    print("   • Conservative destinations (Pakistan, Saudi Arabia, Iran)")
    print("   • Hot climates (Dubai, India summer)")
    print("   • Cold weather (Pakistan mountains, Japan winter)")
    print("   • Cultural events (Eid, Diwali, weddings)")
    print("   • Business travel (formal wear filtering)")
    print("   • Religious sites (modest clothing)")
    
    print("\n" + "=" * 60)
    print("🔥 READY FOR COMPREHENSIVE TESTING!")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
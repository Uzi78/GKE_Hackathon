# weather_service.py
import requests
import json
from typing import Dict, Optional
import logging
import os

class WeatherService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.logger = logging.getLogger(__name__)
    
    def get_weather_forecast(self, city: str, country: str = None) -> Optional[Dict]:
        """
        Fetch 5-day weather forecast for a destination
        """
        try:
            # Construct query string
            query = f"{city},{country}" if country else city
            
            url = f"{self.base_url}/forecast"
            params = {
                'q': query,
                'appid': self.api_key,
                'units': 'metric',  # Celsius
                'cnt': 8  # 1 day forecast (3-hour intervals)
            }
            
            self.logger.info(f"Fetching weather for: {query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather info
            weather_summary = {
                'city': data['city']['name'],
                'country': data['city']['country'],
                'forecasts': []
            }
            
            for forecast in data['list']:
                weather_summary['forecasts'].append({
                    'datetime': forecast['dt_txt'],
                    'temperature': forecast['main']['temp'],
                    'feels_like': forecast['main']['feels_like'],
                    'humidity': forecast['main']['humidity'],
                    'description': forecast['weather'][0]['description'],
                    'main': forecast['weather'][0]['main'],
                    'wind_speed': forecast['wind']['speed']
                })
            
            self.logger.info(f"Successfully fetched weather for {city}")
            return weather_summary
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Weather API error: {e}")
            return self._get_mock_weather(city)
        except Exception as e:
            self.logger.error(f"Unexpected error in weather service: {e}")
            return self._get_mock_weather(city)
    
    def _get_mock_weather(self, city: str) -> Dict:
        """Fallback mock weather data"""
        self.logger.info(f"Using mock weather data for {city}")
        return {
            'city': city,
            'country': 'Unknown',
            'forecasts': [{
                'datetime': '2024-10-15 12:00:00',
                'temperature': 20.0,
                'feels_like': 22.0,
                'humidity': 65,
                'description': 'partly cloudy',
                'main': 'Clouds',
                'wind_speed': 3.5
            }],
            'mock': True
        }
    
    def get_weather_summary(self, city: str, country: str = None) -> str:
        """Get a text summary of weather conditions"""
        weather_data = self.get_weather_forecast(city, country)
        if not weather_data or not weather_data.get('forecasts'):
            return f"Weather data unavailable for {city}"
        
        forecast = weather_data['forecasts'][0]
        temp = forecast['temperature']
        description = forecast['description']
        
        # Create contextual summary
        if temp < 10:
            temp_desc = "cold"
        elif temp > 25:
            temp_desc = "warm"
        else:
            temp_desc = "mild"
        
        return f"{temp_desc} weather around {temp}°C with {description}"
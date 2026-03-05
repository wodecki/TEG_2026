"""
Weather Server - MCP server providing weather data from OpenWeatherMap.
Requires OPENWEATHERMAP_API_KEY environment variable.
"""

import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

if not API_KEY:
    raise ValueError("OPENWEATHERMAP_API_KEY environment variable is required")

async def make_weather_request(url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """Make a request to the OpenWeatherMap API with proper error handling."""
    params["appid"] = API_KEY
    params["units"] = "metric"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Request error: {e}")
            return None

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get 5-day weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    url = f"{OPENWEATHER_API_BASE}/forecast"
    params = {
        "lat": latitude,
        "lon": longitude
    }

    data = await make_weather_request(url, params)

    if not data or "list" not in data:
        return "Unable to fetch forecast data for this location."

    # Format the forecast
    city_name = data.get("city", {}).get("name", "Unknown location")
    forecasts = [f"5-Day Forecast for {city_name}:"]

    # Group by day and take one forecast per day (midday forecast)
    seen_dates = set()
    for item in data["list"]:
        date = item["dt_txt"].split()[0]
        time = item["dt_txt"].split()[1]

        # Take midday forecast (12:00:00) or first forecast of the day
        if date not in seen_dates and (time == "12:00:00" or len(seen_dates) < 5):
            seen_dates.add(date)
            weather = item["weather"][0]
            temp = item["main"]
            wind = item["wind"]

            forecast = f"""
Date: {date} {time}
Temperature: {temp['temp']}°C (feels like {temp['feels_like']}°C)
Weather: {weather['main']} - {weather['description']}
Humidity: {temp['humidity']}%
Wind: {wind['speed']} m/s
"""
            forecasts.append(forecast)

            if len(seen_dates) >= 5:
                break

    return "\n---\n".join(forecasts)

@mcp.tool()
async def get_current_conditions(latitude: float, longitude: float) -> str:
    """Get current weather conditions for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    url = f"{OPENWEATHER_API_BASE}/weather"
    params = {
        "lat": latitude,
        "lon": longitude
    }

    data = await make_weather_request(url, params)

    if not data:
        return "Unable to fetch weather data for this location."

    # Extract weather information
    location_name = data.get("name", "Unknown location")
    weather = data["weather"][0]
    main = data["main"]
    wind = data["wind"]
    clouds = data.get("clouds", {})
    sys_info = data.get("sys", {})

    return f"""
Current Weather in {location_name}:
Temperature: {main['temp']}°C (feels like {main['feels_like']}°C)
Weather: {weather['main']} - {weather['description']}
Humidity: {main['humidity']}%
Pressure: {main['pressure']} hPa
Wind Speed: {wind['speed']} m/s
Wind Direction: {wind.get('deg', 'N/A')}°
Cloudiness: {clouds.get('all', 'N/A')}%
Sunrise: {sys_info.get('sunrise', 'N/A')}
Sunset: {sys_info.get('sunset', 'N/A')}
"""

@mcp.tool()
async def get_weather_by_city(city: str, country_code: str = "") -> str:
    """Get current weather for a city by name.

    Args:
        city: City name (e.g., "London", "New York")
        country_code: Optional ISO 3166 country code (e.g., "GB", "US")
    """
    url = f"{OPENWEATHER_API_BASE}/weather"
    query = f"{city},{country_code}" if country_code else city
    params = {"q": query}

    data = await make_weather_request(url, params)

    if not data:
        return f"Unable to fetch weather data for {city}."

    # Extract weather information
    location_name = data.get("name", city)
    country = data.get("sys", {}).get("country", "")
    weather = data["weather"][0]
    main = data["main"]
    wind = data["wind"]

    return f"""
Current Weather in {location_name}, {country}:
Temperature: {main['temp']}°C (feels like {main['feels_like']}°C)
Weather: {weather['main']} - {weather['description']}
Humidity: {main['humidity']}%
Pressure: {main['pressure']} hPa
Wind Speed: {wind['speed']} m/s
Coordinates: lat={data['coord']['lat']}, lon={data['coord']['lon']}
"""

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
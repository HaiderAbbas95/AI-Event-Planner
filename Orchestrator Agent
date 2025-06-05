import requests
from datetime import datetime, timedelta
import os

# --- Weather Code Descriptions ---
WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle", 61: "Slight rain", 63: "Moderate rain",
    65: "Heavy rain", 66: "Light freezing rain", 67: "Heavy freezing rain", 71: "Slight snow fall",
    73: "Moderate snow fall", 75: "Heavy snow fall", 77: "Snow grains", 80: "Slight rain showers",
    81: "Moderate rain showers", 82: "Violent rain showers", 85: "Slight snow showers",
    86: "Heavy snow showers", 95: "Thunderstorm", 96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# --- Get Coordinates from Google Maps ---
def get_coordinates(city):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city, "key": os.getenv("GOOGLE_API_KEY")}
    response = requests.get(url, params=params)
    data = response.json()
    if not data.get("results"):
        raise Exception(f"Could not determine coordinates for: {city}")
    location = data["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]

# --- Get Forecast from Open-Meteo ---
def get_open_meteo_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_min,temperature_2m_max,weathercode",
        "timezone": "auto",
        "forecast_days": 16
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("daily", {})

# --- Extract Event Dates from Schedule ---
def extract_event_dates(schedule, event_start_date):
    try:
        base_date = datetime.strptime(event_start_date, "%Y-%m-%d")
    except ValueError:
        raise Exception("Event start date must be in YYYY-MM-DD format.")

    return [(base_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(len(schedule))]

# --- Filter Forecast for Event Dates ---
def filter_forecast(forecast_data, event_dates):
    filtered = []
    for date, t_min, t_max, code in zip(
        forecast_data.get("time", []),
        forecast_data.get("temperature_2m_min", []),
        forecast_data.get("temperature_2m_max", []),
        forecast_data.get("weathercode", [])
    ):
        if str(date).strip() in [d.strip() for d in event_dates]:
            filtered.append({
                "date": date,
                "min_temp": f"{t_min}°C",
                "max_temp": f"{t_max}°C",
                "description": WEATHER_CODE_DESCRIPTIONS.get(code, "Unknown")
            })
    return filtered

# --- Main Weather Agent ---
def weather_predictor_agent(user_intent: dict, schedule: list) -> list:
    city = user_intent.get("location")
    event_start_date = user_intent.get("event_date")

    if not city or not event_start_date:
        raise Exception("User intent must include both 'location' and 'event_date'.")

    lat, lon = get_coordinates(city)
    forecast_data = get_open_meteo_forecast(lat, lon)
    event_dates = extract_event_dates(schedule, event_start_date)
    return filter_forecast(forecast_data, event_dates)

# --- Test Block ---
if __name__ == "__main__":
    try:
        user_intent = extracted_intent
        print("\n🌤️ Fetching weather forecast (Open-Meteo)...")
        forecast = weather_predictor_agent(user_intent, schedule)

        print("\n📆 Weather Forecast for Event Days:")
        if not forecast:
            print("No forecast available.")
        else:
            for day in forecast:
                print(f"{day['date']}: 🌤️ {day['description']}")
                print(f"    🌡️ Temp: {day['min_temp']} to {day['max_temp']}")

    except Exception as e:
        print(f"❌ Error in Weather Agent: {e}")

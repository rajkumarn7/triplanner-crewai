from fastapi import FastAPI
import random

app = FastAPI()

# Predefined weather conditions
weather_conditions = [
    {"condition": "Sunny", "temperature": random.randint(28, 35), "icon": "☀️"},
    {"condition": "Rainy", "temperature": random.randint(18, 24), "icon": "🌧️"},
    {"condition": "Cloudy", "temperature": random.randint(22, 28), "icon": "☁️"},
    {"condition": "Stormy", "temperature": random.randint(20, 25), "icon": "⛈️"},
    {"condition": "Snowy", "temperature": random.randint(-5, 3), "icon": "❄️"},
    {"condition": "Foggy", "temperature": random.randint(10, 18), "icon": "🌫️"},
    {"condition": "Windy", "temperature": random.randint(15, 22), "icon": "🌬️"},
    {"condition": "Hazy", "temperature": random.randint(20, 27), "icon": "🌁"},
    {"condition": "Thunderstorm", "temperature": random.randint(18, 23), "icon": "⚡"},
    {"condition": "Drizzle", "temperature": random.randint(19, 23), "icon": "🌦️"},
]

@app.get("/weather")
def get_mock_weather(city: str):
    """Returns a mock weather response based on a random selection."""
    mock_weather = random.choice(weather_conditions)
    return {
        "source": "Mock API",
        "city": city,
        "temperature": mock_weather["temperature"],
        "condition": mock_weather["condition"],
        "icon": mock_weather["icon"]
    }

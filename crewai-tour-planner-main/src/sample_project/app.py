import streamlit as st
import requests
import os
from dotenv import load_dotenv
from crewai import Task, Crew
from crew import TourPlanningProject

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # Store WeatherAPI Key in .env

# Function to fetch current weather
def get_current_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "icon": data["current"]["condition"]["icon"]
        }
    return None

# Function to fetch seasonal weather
def get_seasonal_weather(city, season):
    # Mapping seasons to approximate months
    season_months = {
        "Spring": "03-15",
        "Summer": "06-15",
        "Fall": "09-15",
        "Winter": "12-15"
    }
    
    if season not in season_months:
        return None
    
    url = f"http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={city}&dt=2024-{season_months[season]}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["forecast"]["forecastday"][0]["day"]["avgtemp_c"],
            "condition": data["forecast"]["forecastday"][0]["day"]["condition"]["text"],
            "icon": data["forecast"]["forecastday"][0]["day"]["condition"]["icon"]
        }
    return None

# Streamlit UI
def main():
    st.title("AI Tour Planner with Weather Insights")

    # Input fields
    st.header("Trip Details")
    destination = st.text_input("Destination")
    start_date = st.date_input("Start Date")
    duration = st.number_input("Duration (days)", min_value=1, max_value=30, value=7)
    budget = st.number_input("Budget ($)", min_value=100, value=1000)

    # Preferences
    st.header("Preferences")
    interests = st.multiselect(
        "Select your interests",
        ["Culture", "Food", "Adventure", "Nature", "Shopping", "History"]
    )

    if destination:
        # Fetch current weather
        weather = get_current_weather(destination)
        if weather:
            st.header(f"Current Weather in {destination}")
            st.image(f"http:{weather['icon']}")
            st.write(f"**Temperature:** {weather['temperature']}°C")
            st.write(f"**Condition:** {weather['condition']}")
        else:
            st.warning("Could not fetch current weather.")

        # Fetch and display seasonal weather
        st.header(f"Seasonal Weather in {destination}")
        seasons = ["Spring", "Summer", "Fall", "Winter"]
        for season in seasons:
            season_weather = get_seasonal_weather(destination, season)
            if season_weather:
                st.subheader(f"{season}:")
                st.image(f"http:{season_weather['icon']}")
                st.write(f"**Avg Temperature:** {season_weather['temperature']}°C")
                st.write(f"**Condition:** {season_weather['condition']}")
            else:
                st.warning(f"Weather data for {season} is unavailable.")

    if st.button("Generate Trip Plan"):
        if destination:
            with st.spinner('Generating your perfect trip plan...'):
                try:
                    # Initialize the crew
                    project = TourPlanningProject()
                    
                    # Create the task
                    task = Task(
                        description=f"""
                        Plan a trip to {destination} for {duration} days starting {start_date}.
                        Budget: ${budget}
                        Interests: {', '.join(interests)}
                        """,
                        expected_output="A detailed travel plan including recommendations based on the provided preferences and budget.",
                        agent=project.tour_planner()
                    )
                    
                    # Get the crew and run
                    crew = Crew(
                        agents=[project.tour_planner()],
                        tasks=[task],
                        verbose=True
                    )
                    result = crew.kickoff()
                    
                    # Display results
                    st.success("Trip Plan Generated!")
                    st.write(result)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.error("Please enter a destination")

if __name__ == "__main__":
    main()

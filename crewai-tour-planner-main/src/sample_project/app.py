__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from crewai import Task, Crew
from crew import TourPlanningProject
import streamlit as st

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
    season_months = {"Spring": "2025-03-15", "Summer": "2024-06-15", "Fall": "2024-09-15", "Winter": "2024-12-15"}
    if season not in season_months:
        return None

    url = f"http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={city}&dt={season_months[season]}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["forecast"]["forecastday"][0]["day"]["avgtemp_c"],
            "condition": data["forecast"]["forecastday"][0]["day"]["condition"]["text"],
            "icon": data["forecast"]["forecastday"][0]["day"]["condition"]["icon"]
        }
    return None

# Function to fetch mock weather
def get_mock_weather(city, scenario="sunny_day"):
    mock_weather_data = {
        "sunny_day": {
            "temperature": 28,
            "condition": "Sunny",
            "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png"
        },
        "rainy_day": {
            "temperature": 18,
            "condition": "Moderate rain",
            "icon": "//cdn.weatherapi.com/weather/64x64/day/302.png"
        },
        "snowy_day": {
            "temperature": -2,
            "condition": "Light snow",
            "icon": "//cdn.weatherapi.com/weather/64x64/day/326.png"
        },
        "storm": {
            "temperature": 22,
            "condition": "Thunderstorm",
            "icon": "//cdn.weatherapi.com/weather/64x64/day/200.png"
        }
    }
    return mock_weather_data.get(scenario.lower().replace(' ', '_'))

# Streamlit UI
def main():
    st.set_page_config(page_title="AI Tour Planner", page_icon="🌍", layout="wide")

    st.markdown("<h1 class='center-text'>🌍 DEEPWEAVER AI TRIP PLANNER FOR SMARTVISIT</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Trip Input Section
    st.header("📝 Plan Your Trip")

    # Add Weather API Selection
    col1, col2 = st.columns([1, 2])
    with col1:
        use_mock_api = st.toggle("Use Mock Weather API", value=False)
    with col2:
        if use_mock_api:
            mock_api_option = st.selectbox(
                "Select Mock Weather Scenario",
                ["Sunny Day", "Rainy Day", "Snowy Day", "Storm"]
            )

    col1, col2, col3 = st.columns(3)
    with col1:
        destination = st.text_input("📍 Destination")
    with col2:
        start_date = st.date_input("📆 Start Date")
    with col3:
        duration = st.number_input("🕒 Duration (days)", min_value=1, max_value=30, value=7)

    budget = st.slider("💰 Budget ($)", min_value=100, max_value=5000, value=1000, step=100)

    # Preferences
    interests = st.multiselect(
        "🎯 Select Your Interests",
        ["Culture", "Food", "Adventure", "Nature", "Shopping", "History"]
    )

    st.markdown("---")

    # Initialize session state for chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "crew" not in st.session_state:
        st.session_state.crew = None

    if "initial_response_fetched" not in st.session_state:
        st.session_state.initial_response_fetched = False

    if "loading" not in st.session_state:
        st.session_state.loading = False

    if "user_input" not in st.session_state:
        st.session_state.user_input = ''

    if "user_response_fetched" not in st.session_state:
        st.session_state.user_response_fetched = False

    if "prev_user_message" not in st.session_state:
        st.session_state.prev_user_message = ""
    
    # Modify the weather fetching section
    if st.button("🚀 Generate Trip Plan", key="generate"):
        if destination:
            with st.spinner('🔄 Fetching weather data and generating your trip plan...'):
                try:
                    # Fetch Weather Data based on API selection
                    if use_mock_api:
                        scenario = mock_api_option.lower().replace(' ', '_')
                        current_weather = get_mock_weather(destination, scenario)
                        st.session_state["real_weather"] = current_weather
                        st.session_state["mock_weather"] = current_weather
                        
                        # Use mock data for seasonal weather
                        st.session_state["seasonal_weather"] = {
                            "Spring": get_mock_weather(destination, "sunny_day"),
                            "Summer": get_mock_weather(destination, "sunny_day"),
                            "Fall": get_mock_weather(destination, "rainy_day"),
                            "Winter": get_mock_weather(destination, "snowy_day")
                        }
                    else:
                        current_weather = get_current_weather(destination)
                        st.session_state["real_weather"] = current_weather
                        st.session_state["mock_weather"] = None
                        
                        # Fetch real seasonal weather data
                        st.session_state["seasonal_weather"] = {
                            season: get_seasonal_weather(destination, season) 
                            for season in ["Spring", "Summer", "Fall", "Winter"]
                        }

                    # Display Weather Data First
                    st.markdown("## 🌦 Weather Information")
                    col1, col2 = st.columns(2)

                    with col1:
                        weather = st.session_state["real_weather"]
                        if weather:
                            st.markdown(f"### 🌍 Current Weather in {destination} (Real API)")
                            st.image(f"http:{weather['icon']}", width=80)
                            st.write(f"**Temperature:** {weather['temperature']}°C")
                            st.write(f"**Condition:** {weather['condition']}")

                    with col2:
                        mock_weather = st.session_state["mock_weather"]
                        if mock_weather:
                            st.markdown(f"### 🏷 Today's Weather in {destination} (Mock API)")
                            st.write(f"🌤 **{mock_weather['icon']} {mock_weather['condition']}**")
                            st.write(f"**Temperature:** {mock_weather['temperature']}°C")

                    # Seasonal Weather Display (Side-by-Side Flex Layout)
                    if st.session_state["seasonal_weather"]:
                        st.markdown("### 📅 Seasonal Weather")

                        # Create four columns for Spring, Summer, Fall, and Winter
                        col1, col2, col3, col4 = st.columns(4)

                        seasons = ["Spring", "Summer", "Fall", "Winter"]
                        cols = [col1, col2, col3, col4]

                        for season, col in zip(seasons, cols):
                            season_weather = st.session_state["seasonal_weather"].get(season)
                            if season_weather:
                                with col:
                                    st.markdown(f"#### {season}")
                                    st.image(f"http:{season_weather['icon']}", width=80)
                                    st.write(f"**Avg Temp:** {season_weather['temperature']}°C")
                                    st.write(f"**Condition:** {season_weather['condition']}")
                            else:
                                with col:
                                    st.warning(f"{season} data unavailable.")

                    # Trip Planning
                    st.markdown("---")
                    st.markdown("## 🗺 Your Travel Itinerary")

                    # Initialize the crew
                    project = TourPlanningProject()
                    weather_info = f"""
                        Current Weather: Temperature: {current_weather.get('temperature', 'N/A')}°C, Condition: {current_weather.get('condition', 'N/A')}
                        """
                    agent = project.tour_planner()
                    st.session_state.agent = agent
                    st.session_state.initial_details = f"""
                        Plan a trip to {destination} for {duration} days starting {start_date}.
                        Budget: ${budget}
                        Interests: {', '.join(interests)}
                        
                        Weather Information:
                        Current Weather: {weather_info}
                        Seasonal Weather:
                        Spring: Temperature: {st.session_state['seasonal_weather']['Spring']['temperature']}°C, Condition: {st.session_state['seasonal_weather']['Spring']['condition']}
                        Summer: Temperature: {st.session_state['seasonal_weather']['Summer']['temperature']}°C, Condition: {st.session_state['seasonal_weather']['Summer']['condition']}
                        Fall: Temperature: {st.session_state['seasonal_weather']['Fall']['temperature']}°C, Condition: {st.session_state['seasonal_weather']['Fall']['condition']}
                        Winter: Temperature: {st.session_state['seasonal_weather']['Winter']['temperature']}°C, Condition: {st.session_state['seasonal_weather']['Winter']['condition']}
                        
                        Please consider the current and seasonal weather conditions when planning activities. 
                        Suggest indoor alternatives for bad weather and outdoor activities for good weather.
                        Make appropriate recommendations based on the temperature and conditions.
                        """
                    
                    task = Task(
                        description=st.session_state.initial_details,
                        expected_output="A detailed travel plan including weather-appropriate recommendations based on the provided preferences, budget, and current/seasonal weather conditions.",
                        agent=agent
                    )

                    # Get the crew and run
                    st.session_state.crew = Crew(
                        agents=[agent],
                        tasks=[task],
                        verbose=True
                    )
                    result = st.session_state.crew.kickoff()

                    st.session_state.initial_response_fetched = True
                    st.success("🎉 Trip Plan Generated!")
                    trip_plan = getattr(result, "raw", "❌ No trip plan generated. Please try again.")
                    st.markdown("")

                    st.session_state.chat_history.append(("AI", trip_plan))

                except Exception as e:
                    st.error(f"⚠️ An error occurred: {str(e)}")
        else:
            st.error("❌ Please enter a destination")

    if st.session_state.initial_response_fetched:
        # Display chat history
        st.write("Travel Recommendations")
        for role, message in st.session_state.chat_history:
            if role == "User":
                # Right-aligned, grey background for User messages
                st.markdown(f"""
                <div style="text-align: right; background-color: #f0f0f5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    {message}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Left-aligned (default) for AI messages
                st.markdown(f"""
                <div style="background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    {message}
                </div>
                """, unsafe_allow_html=True)


        # Chatbox for conversation continuation
        if st.session_state.user_response_fetched:
            st.session_state.user_response_fetched = False
            st.session_state.user_input = ''

        user_message = st.text_area("Continue the conversation:", "", key="user_input")
        
        if st.session_state.loading:
            st.button("Submit", disabled=True)
        else:
            #if st.button("Submit") or (st.session_state.prev_user_message != user_message):
            if st.button("Submit"):
                st.session_state.prev_user_message = user_message

                if user_message.strip() and st.session_state.crew:
                    st.session_state.loading = True
                    with st.spinner('🔄 Updating trip plan...'):
                        st.session_state.chat_history.append(("User", user_message))
                        #st.rerun()  # Refresh UI to display updated chat history
                        
                        conversation_context = "\n".join(
                            [f"{role}: {message}" for role, message in st.session_state.chat_history]
                        )

                        conversation_context = "Initial Request:"  + st.session_state.initial_details + "\n" + conversation_context

                        # Call CrewAI for the next response
                        follow_up_task = Task(
                            description=conversation_context,
                            agent=st.session_state.agent,  # Use the same agent
                            expected_output="A well-structured travel itinerary."
                        )

                        # Add the new task to the Crew
                        st.session_state.crew.tasks = [follow_up_task]

                        # Run CrewAI with the new task
                        response = st.session_state.crew.kickoff()

                        st.session_state.chat_history.append(("AI", response))
                        st.session_state.loading = False
                        st.session_state.user_response_fetched = True
                        st.rerun()  # Refresh UI to display updated chat history

                elif not st.session_state.crew:
                    st.error("Please submit the trip details first before continuing the chat.")

if __name__ == "__main__":
    main()

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from crewai import Task, Crew
from crew import TourPlanningProject
import content_validator as Validator

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

    # location = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition((pos) => pos.coords)", want_output=True)
    # print(location)

    # Inject custom CSS for tab styling
    st.markdown(
        """
        <style>
            div[data-baseweb="tab-list"] {
                
            }
            button[data-baseweb="tab"] {
                padding: 5px 35px !important;  /* Increase padding */
            }
            button[data-baseweb="tab"] p {
                font-size: 25px !important;  /* Increase font size */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "window_selected" not in st.session_state:
        st.session_state.window_selected = "Chat"
    
    if "window_type" not in st.session_state:
        st.session_state.window_type = ""
    
    if "parsed_content" not in st.session_state:
        st.session_state.parsed_content = {}

    if "pre_chat_history" not in st.session_state:
        st.session_state.pre_chat_history = []
        st.session_state.pre_chat_history.append(("AI", "Welcome to Athens, How can I help you?"))
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "crew" not in st.session_state:
        st.session_state.crew = None

    if "initial_response_fetched" not in st.session_state:
        st.session_state.initial_response_fetched = False

    if "loading" not in st.session_state:
        st.session_state.loading = False

    if "user_input_chat" not in st.session_state:
        st.session_state.user_input_chat = ''
    
    if "user_input_plan" not in st.session_state:
        st.session_state.user_input_plan = ''

    if "user_response_fetched" not in st.session_state:
        st.session_state.user_response_fetched = False

    if "prev_user_message" not in st.session_state:
        st.session_state.prev_user_message = ""
    

    tab1, tab2 = st.tabs(["Chat", "Plan"])
    with tab1:
        chat_trip()
    with tab2:
        plan_trip()

def chat_trip():
    st.header("Conversation")

    chatConversations()
    userChatArea()
    submitBtn()

def plan_trip():
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

    # Modify the weather fetching section
    generate_btn = st.button("🚀 Generate Trip Plan", key="generate")
    if generate_btn:
        if destination:
            st.session_state.window_type = "Plan"
            st.session_state.window_selected = "Plan"
            st.session_state.pre_chat_history = []
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
                    weather_info = f"""
                        Current Weather: Temperature: {current_weather.get('temperature', 'N/A')}°C, Condition: {current_weather.get('condition', 'N/A')}
                        """
                    
                    initializeAgent()
                    
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
                        agent=st.session_state.agent
                    )

                    # Get the crew and run
                    st.session_state.crew = Crew(
                        agents=[st.session_state.agent],
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
        
        chatConversations()
        userChatArea()
        submitBtn()

def chatConversations():
    for chat_history in [st.session_state.pre_chat_history, st.session_state.chat_history]:
        for role, message in chat_history:
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

def userChatArea():
    # Chatbox for conversation continuation
    if st.session_state.user_response_fetched:
        st.session_state.user_response_fetched = False
        st.session_state.user_input_chat = ''
        st.session_state.user_input_plan = ''

    text_area_key = "user_input_chat"
    if st.session_state.window_type == "Plan":
        text_area_key = "user_input_plan"

    user_message = st.text_area("Continue the conversation:", "", key=text_area_key)
    st.session_state.user_message = user_message

def initializeAgent():
    if "agent" not in st.session_state:
        project = TourPlanningProject()
        st.session_state.agent = project.tour_planner()

def submitBtn():

    submit_btn_key = "submit_chat"
    if st.session_state.window_type == "Plan":
        submit_btn_key = "submit_plan"

    if st.session_state.loading:
        st.button("Submit", disabled=True, key=submit_btn_key)
    
    else:
        #if st.button("Submit", key=submit_btn_key) or (st.session_state.prev_user_message != user_message):
        if st.button("Submit", key=submit_btn_key):
            user_message = st.session_state.user_message
            st.session_state.prev_user_message = user_message

            if st.session_state.window_type == "" and st.session_state.window_selected == "Chat":
                st.session_state.window_type = "Chat"

            if st.session_state.window_type == "Chat" and st.session_state.crew is None:
                # if details haven't provided, then st.rerun() breaks the session code further
                parseChatRequestAndProceed(user_message)
                
                initializeAgent()

                st.session_state.crew = Crew(
                    agents=[st.session_state.agent],
                    tasks=[],
                    verbose=True
                )
            
            if user_message.strip() and st.session_state.crew:
                st.session_state.loading = True
                with st.spinner('🔄 Updating trip plan...'):
                    st.session_state.chat_history.append(("User", user_message))
                    #st.rerun()  # Refresh UI to display updated chat history
                    
                    conversation_context = "\n".join(
                        [f"{role}: {message}" for role, message in st.session_state.chat_history]
                    )

                    if st.session_state.window_type == "Plan":
                        conversation_context = "Initial Request:"  + st.session_state.initial_details + "\n" + conversation_context

                    if st.session_state.window_type == "Plan":
                        task_expected_output = "A well-structured travel itinerary."
                    else:
                        # task_expected_output = "A well-structured travel itinerary is shown only after the user provided destination, start date, budget and no of days of travel. Don't show the itineray or suggest anything till they provided these details."
                        task_expected_output = """
                                Initially provide - a table-structured travel itinerary, after that make changes or provide recommendations only.
                                If they inquired about bus travels then recommend BigBusTours (https://www.bigbustours.com/en/athens/athens-bus-tours) else don't say about it.
                                If last asked question is not about itinerary and any other request, then response only for that and don't show full itinerary unless explicity requested.
                                If user asks about customizing plan such as cheap options, suggest travel guide - Response like connect to live travel agent.
                                If user asks you to do something like book bus or if your response is similiar to 'I am an AI' instead Response like connect to live travel agent. 
                                Importantly don't mention I am an AI, instead I can help you by redirecting to live travel agent or request a call back later
                                """
                        
                        # Only after the customer asks to redirect to live agent, show summarize content with budget, no. of days, start date, interests and itinerary plan.
                                
                                
                    # Call CrewAI for the next response
                    follow_up_task = Task(
                        description=conversation_context,
                        agent=st.session_state.agent,  # Use the same agent
                        expected_output=task_expected_output
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

def parseChatRequestAndProceed(user_message):

    st.session_state.loading = True
    with st.spinner('🔄 Updating trip plan...'):
        conversation_context = "\n".join(
            [f"{role}: {message}" for role, message in st.session_state.pre_chat_history]
        )
        conversation_context += "\n" + "User: " + user_message
        parsedContent = Validator.parseContent(conversation_context)

        follow_up_question = []

        # if "destination" not in parsedContent or parsedContent["destination"] is None:
        #     follow_up_question.append("What is your Destination? ")

        if "start_date" not in parsedContent or parsedContent["start_date"] is None:
            follow_up_question.append("What is your Start Date? ")

        if "budget" not in parsedContent or parsedContent["budget"] is None:
            follow_up_question.append("What is your Budget? ")
        if "no_of_days" not in parsedContent or parsedContent["no_of_days"] is None:
            follow_up_question.append("For how many days you plan this trip? ")
        
        print(follow_up_question)

        if len(follow_up_question) == 0:
            for role, message in st.session_state.pre_chat_history:
                st.session_state.chat_history.append((role, message))

            st.session_state.pre_chat_history = []
            st.session_state.loading = False
        else:
            follow_up_question = "\n".join(x for x in follow_up_question)
            st.session_state.pre_chat_history.append(("User", user_message))
            st.session_state.pre_chat_history.append(("AI", follow_up_question))
            st.session_state.loading = False
            st.session_state.user_response_fetched = True
            st.rerun()

if __name__ == "__main__":
    main()

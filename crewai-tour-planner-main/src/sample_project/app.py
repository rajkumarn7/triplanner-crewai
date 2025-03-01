import streamlit as st
from crewai import Task, Crew
from crew import TourPlanningProject
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("GEMINI_API_KEY")
def main():
    st.title("AI Tour Planner")
    
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
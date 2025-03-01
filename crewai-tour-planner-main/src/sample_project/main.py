#!/usr/bin/env python
import sys
import warnings
from datetime import datetime

from sample_project.crew import TourPlanningProject

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def get_user_input():
    """
    Get user input for the city they want information about.
    """
    city = input("Enter the city you want to explore: ").strip()
    return city

def run():
    """
    Run the crew based on user input.
    """
    destination = get_user_input()

    inputs = {
        'destination': destination,
        'current_year': str(datetime.now().year)
    }

    try:
        print(f"\n🚀 Planning a trip to {destination}... Please wait.\n")
        TourPlanningProject().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    destination = get_user_input()

    inputs = {
        "destination": destination
    }
    try:
        TourPlanningProject().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        TourPlanningProject().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and return the results.
    """
    destination = get_user_input()

    inputs = {
        "destination": destination
    }
    try:
        TourPlanningProject().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    run()

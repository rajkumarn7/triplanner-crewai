import os
from dotenv import load_dotenv
from crewai import Task, Crew, Agent
from crewai.project import CrewBase, agent, task
import json
from datetime import datetime

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("GEMINI_API_KEY")

@CrewBase
class ValidatorAgent():
	"""Tour Planning Project - Initial Request Validator"""

	agents_config = 'config/agents_validator.yaml'
	tasks_config = 'config/tasks_validator.yaml'

	@agent
	def validator(self) -> Agent:
		return Agent(config=self.agents_config['validator'], verbose=True)
  
  # @task
  # def validate_task(self) -> Task:
  #   return Task(config=self.tasks_config['validate_task'])

validator_agent = ValidatorAgent().validator()

def parseContent(context):
  # current_date = datetime.today().strftime("%d-%b-%Y")
  current_task = Task(
      description=context,
      agent=validator_agent,  # Use the same agent
      expected_output="Consolidate data and return a json with keys - destination, start_date, budget, no_of_days and other_details. "+
        #"start_date should be converted to dd-MMM-yyyy format. "+ 
        #"Consider today date as " + current_date + ". " + 
        "Rest all summarized data - just key points with comma seperated is set to other_details. " + 
        "Don't need to provide suggestions or look for additional info."
  )
  
  crew = Crew(
      agents=[validator_agent],
      tasks=[],
      verbose=True
  )

  crew.tasks = [current_task]
  response = crew.kickoff()
  response = str(response)
  response = response.strip("`").strip("json").strip()
  response = json.loads(response)

  return response


# context = "Trip to Madurai and Trichy with my wife for honeymoon on this weekend."
# print( parseContent(context) )

# context = "Trip to Madurai with my wife for honeymoon on this weekend."
# print( parseContent(context) )
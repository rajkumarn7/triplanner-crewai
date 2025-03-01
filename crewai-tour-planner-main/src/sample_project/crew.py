from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class TourPlanningProject():
	"""Tour Planning Project crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def tour_planner(self) -> Agent:
		return Agent(config=self.agents_config['tour_planner'], verbose=True)

	# @agent
	# def itinerary_analyst(self) -> Agent:
	# 	return Agent(config=self.agents_config['itinerary_analyst'], verbose=True)

	# @agent
	# def local_guide_expert(self) -> Agent:
	# 	return Agent(config=self.agents_config['local_guide_expert'], verbose=True)

	# @agent
	# def budget_planner(self) -> Agent:
	# 	return Agent(config=self.agents_config['budget_planner'], verbose=True)

	# @agent
	# def logistics_coordinator(self) -> Agent:
	# 	return Agent(config=self.agents_config['logistics_coordinator'], verbose=True)

	# @agent
	# def accommodation_specialist(self) -> Agent:
	# 	return Agent(config=self.agents_config['accommodation_specialist'], verbose=True)

	# @agent
	# def food_dining_expert(self) -> Agent:
	# 	return Agent(config=self.agents_config['food_dining_expert'], verbose=True)

	# @agent
	# def adventure_activities_planner(self) -> Agent:
	# 	return Agent(config=self.agents_config['adventure_activities_planner'], verbose=True)

	# @agent
	# def weather_packing_advisor(self) -> Agent:
	# 	return Agent(config=self.agents_config['weather_packing_advisor'], verbose=True)

	# @agent
	# def emergency_safety_advisor(self) -> Agent:
	# 	return Agent(config=self.agents_config['emergency_safety_advisor'], verbose=True)

	@task
	def research_task(self) -> Task:
		return Task(config=self.tasks_config['research_task'])

	# @task
	# def itinerary_task(self) -> Task:
	# 	return Task(config=self.tasks_config['itinerary_task'], output_file='itinerary.md')

	# @task
	# def accommodation_task(self) -> Task:
	# 	return Task(config=self.tasks_config['accommodation_task'])

	# @task
	# def food_dining_task(self) -> Task:
	# 	return Task(config=self.tasks_config['food_dining_task'])

	# @task
	# def adventure_activities_task(self) -> Task:
	# 	return Task(config=self.tasks_config['adventure_activities_task'])

	# @task
	# def weather_packing_task(self) -> Task:
	# 	return Task(config=self.tasks_config['weather_packing_task'])

	# @task
	# def emergency_safety_task(self) -> Task:
	# 	return Task(config=self.tasks_config['emergency_safety_task'])

	@crew
	def crew(self) -> Crew:
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)

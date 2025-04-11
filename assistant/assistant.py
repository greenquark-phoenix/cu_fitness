import json
from datetime import date
from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from service.service import ProfileService, WorkoutService, NutritionService, ScheduleService

_SYSTEM_MESSAGE = SystemMessage("""
You are a highly intelligent, empathetic, and motivational AI fitness assistant. Your goal is to provide deeply personalized, safe, and effective fitness and nutrition guidance to users. You act as a supportive coach, gathering the right data and offering tailored plans that align with each user’s goals and lifestyle.

Responsibilities:

0. Load the user's profile:
- Use the _get_basic_info() and _get_dietary_info() tools to retrieve the user's physical details and dietary preferences.
- Show the user their profile information and ask for confirmation to proceed.

1. Information Gathering:
- Fitness goals: weight loss, muscle gain, endurance, etc.

2. Goal-Oriented Planning:
- Require users to provide a start date and number of weeks to achieve their goal.
- Assess whether the goal is realistic within the timeframe.
- Ensure all recommendations prioritize safety and medical considerations.

3. Workout Recommendations:
- Use _get_available_workouts() to retrieve workout sub-plans.
- Recommend one or more sub-plans, from the available workouts, based on the user’s fitness goal.
- For each plan, include:
  - Focus area (e.g., strength, cardio, flexibility)
  - Weekly schedule with session duration and frequency
  - Required equipment or environment (home/gym/outdoor)
  - Benefits and tips

4. Meal Planning:
- Use _get_available_meals() and dietary data to build a compatible meal plan.
- For each meal:
  - Match dietary preferences and allergies
  - Include ingredients and macronutrient breakdown
  - Align meals with the workout plan
  - Offer flexible substitutions if applicable

5. Scheduling:
- Use _add_schedule(start_date, num_weeks, meals, workouts) only after receiving explicit user approval.
- Format the workouts as a list of json objects with the following fields:
    - day, e.g., "Monday"
    - name, e.g., "Dumbbell-Only Starter"

6. User Interaction:
- Keep the tone friendly, professional, and encouraging.
- Ask clarifying questions as needed.
- Respond to feedback and adapt plans accordingly.
- Motivate users and acknowledge progress.

Response Formatting:
Format your responses using HTML for readability. Use:
- <h2> for headings
- <p> for paragraphs
- <ul>/<li> for lists
- <strong> for emphasis
- <div> to group content
- <br> for line breaks

Ensure responses are easy to navigate and visually structured.
""")


def _create_get_basic_info_tool(username: str):
    @tool
    def _get_basic_info():
        """Retrieves the physical details: height, weight, gender, and age"""
        print("Retrieving the physical details")
        return ProfileService.get_basic_info(username=username)

    return _get_basic_info


def _create_get_dietary_info_tool(username: str):
    @tool
    def _get_dietary_info():
        """Retrieves dietary preferences or allergies"""
        print("Retrieving dietary info")
        return ProfileService.get_dietary_info(username=username)

    return _get_dietary_info


def _create_get_available_workouts_tool():
    @tool
    def _get_available_workouts():
        """Retrieve available workouts"""
        print("Retrieving available workouts")
        return WorkoutService.get_available_workouts()

    return _get_available_workouts


def _create_get_available_meals_tool():
    @tool
    def _get_available_meals():
        """Retrieve available meals"""
        print("Retrieving available meals")
        return NutritionService.get_available_meals()

    return _get_available_meals


def _create_add_schedule_tool(username: str):
    @tool
    def _add_schedule(start_date: date, num_weeks: int, meals: list[str], workouts: list[json]):
        """Add the meals and workouts to the user's schedule"""
        print(
            f"Adding meals {meals} and workouts {workouts} to the user's schedule, starting from {start_date} for {num_weeks} weeks")
        try:
            ScheduleService.create_schedule(username, start_date, num_weeks, meals, workouts)
        except Exception as e:
            print(e)

    return _add_schedule


class State(TypedDict):
    messages: Annotated[list, add_messages]


class Agent:
    def __init__(self, llm, username: str):
        tools = [_create_get_basic_info_tool(username), _create_get_dietary_info_tool(username),
                 _create_get_available_workouts_tool(), _create_get_available_meals_tool(),
                 _create_add_schedule_tool(username)]
        self.llm = llm.bind_tools(tools)
        self.graph = self._build_graph(tools)

    def stream_graph_update(self, user_input: str, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        human_message = HumanMessage(content=user_input)
        print("User input:", user_input)
        for event in self.graph.stream({"messages": [human_message]}, config):
            for value in event.values():
                message = value["messages"][-1]
                if not isinstance(message, ToolMessage):
                    yield value["messages"][-1].content.replace("```html", "").replace("```", "")

    def _build_graph(self, tools):
        graph_builder = StateGraph(State)
        graph_builder.add_node("llm", self._llm)

        tool_node = ToolNode(tools=tools)
        graph_builder.add_node("tools", tool_node)

        graph_builder.add_edge(START, "llm")
        graph_builder.add_conditional_edges(
            "llm",
            tools_condition,
        )
        graph_builder.add_edge("tools", "llm")

        return graph_builder.compile(checkpointer=MemorySaver())

    def _llm(self, state: State):
        messages = [_SYSTEM_MESSAGE] + state["messages"]
        return {"messages": [self.llm.invoke(messages)]}

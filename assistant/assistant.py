from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from service.service import ProfileService, WorkoutService, NutritionService

_SYSTEM_MESSAGE = SystemMessage("""
You are a highly intelligent and empathetic AI fitness assistant, designed to provide personalized and effective guidance to users seeking to achieve their fitness goals. Your primary role is to act as a knowledgeable coach, gathering comprehensive information about their physical profile, fitness background, and dietary habits to create tailored workout and meal plans.

**Key Responsibilities:**

* **Information Gathering:**
    * Utilize available tools to retrieve and accurately record the user's:
        * Height, weight, and age.
        * Workout history, including frequency, intensity, and preferred activities.
        * Dietary preferences, restrictions, and allergies.
        * Current fitness goals (e.g., weight loss, muscle gain, endurance).
        * Any pre-existing medical conditions that may affect their fitness routines.
        
* **Goal-Oriented Planning:**
    * Before recommending any workout or meal, **require the user to specify a desired time window** for achieving their fitness goals. This ensures realistic and sustainable planning.
    * Prioritize user safety and well-being by acknowledging any health concerns and adjusting recommendations accordingly.
    
* **Workout Recommendations:**
    * Retrieve and present available workouts.
    * Recommend **one specific workout sub-plan at a time**, focusing on clarity and manageability.
    * Provide a **detailed description** of the recommended workout plan, including:
        * The plan's primary focus (e.g., cardiovascular fitness, strength training, flexibility).
        * A suggested schedule (e.g., days of the week, duration of sessions).
        * Key features and benefits of the plan.
        * Any required equipment or location.
    * **Always seek explicit user approval before adding any workout to their schedule.**
    
* **Meal Recommendations:**
    * Retrieve and present available meals, taking into account the user's dietary preferences and allergies.
    * Provide meal suggestions that align with the user's fitness goals and workout plan.
    * Offer nutritional information for each meal, including macronutrient breakdown.
    
* **User Interaction:**
    * Maintain a conversational and encouraging tone.
    * Actively listen to user feedback and adjust recommendations as needed.
    * Ask clarifying questions to ensure accurate understanding of user needs.
    * Provide motivation and support to help users stay on track.

**Available Tools:**

* `_get_basic_info()`: Retrieves the user's basic physical information.
* `_get_dietary_info()`: Retrieves the user's dietary preferences and allergies.
* `_get_available_workouts()`: Retrieves a list of available workout plans.
* `_get_available_meals()`: Retrieves a list of available meal options.
* `_add_workout_sub_plan(workout_sub_plan)`: Adds a workout plan to the user's schedule (requires explicit user approval).

**Response Formatting:**

* Structure responses using HTML for enhanced readability.
* Employ the following HTML tags:
    * `<h2>` for section headers.
    * `<p>` for paragraphs.
    * `<ul>` and `<li>` for lists.
    * `<strong>` for emphasis.
    * `<div>` for general content organization.
    * Add `<br>` tags for line breaks when needed.
""")


def _create_get_basic_info_tool(username: str):
    @tool
    def _get_basic_info():
        """Retrieves height, weight, gender, and age"""
        print("Retrieving basic info")
        return ProfileService.get_basic_info(username=username)

    return _get_basic_info


def _create_get_dietary_info_tool(username: str):
    @tool
    def _get_dietary_info():
        """Retrieves and dietary preferences or allergies"""
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

def _create_add_workouts_tool(username: str):
    @tool
    def _add_workout_sub_plan(workout_sub_plan: str):
        """Add the workouts to the user's schedule"""
        print(f"Adding workout sub plan {workout_sub_plan} to the user's schedule")
        WorkoutService.add_workout(username, workout_sub_plan)

    return _add_workout_sub_plan


class State(TypedDict):
    messages: Annotated[list, add_messages]


class Agent:
    def __init__(self, llm, username: str):
        tools = [_create_get_basic_info_tool(username), _create_get_dietary_info_tool(username),
                 _create_get_available_workouts_tool(), _create_get_available_meals_tool(), _create_add_workouts_tool(username)]
        self.llm = llm.bind_tools(tools)
        self.graph = self._build_graph(tools)

    def stream_graph_update(self, user_input: str, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        human_message = HumanMessage(content=user_input)
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
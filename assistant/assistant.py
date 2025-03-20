from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from service.service import ProfileService, WorkoutService, NutritionService

_SYSTEM_MESSAGE = SystemMessage("""
You are a helpful and knowledgeable AI fitness assistant. Your role is to guide users in achieving their fitness goals by gathering relevant information about their body measurements, workout history, and dietary preferences.

When a user asks for fitness or nutrition advice, use the available tools to:
  * Retrieve their height, weight, and age.
  * Retrieve any dietary preferences or allergies.
  * Retrieve available workouts.
  * Retrieve available meals.

Track body composition and fitness goals (if applicable).
Then, ask clarifying questions to tailor your recommendations. Understand their specific goals, such as increasing strength, reducing body fat, or targeting certain muscle groups.
Ensure that your recommendations are personalized, practical, and aligned with their current habits. Provide guidance on workout techniques, progressive overload, and nutrition principles to help them optimize their results.
Encourage consistency, monitor progress, and adjust recommendations based on user feedback.

Ensure that your responses are formatted in HTML for better readability. Structure responses using:

  * <h2> for section headers
  * <p> for paragraphs
  * <ul> and <li> for lists
  * <strong> for emphasis
  * <div> for others
""")


def _create_get_basic_info(username: str):
    @tool
    def _get_basic_info():
        """Retrieves height, weight, gender, and age"""
        return ProfileService.get_basic_info(username=username)

    return _get_basic_info


def _create_get_dietary_info(username: str):
    @tool
    def _get_dietary_info():
        """Retrieves and dietary preferences or allergies"""
        return ProfileService.get_dietary_info(username=username)

    return _get_dietary_info

def _create_get_available_workouts():
    @tool
    def _get_available_workouts():
        """Retrieve available workouts"""
        return WorkoutService.get_available_workouts()

    return _get_available_workouts

def _create_get_available_meals():
    @tool
    def _get_available_meals():
        """Retrieve available meals"""
        return NutritionService.get_available_meals()

    return _get_available_meals


class State(TypedDict):
    messages: Annotated[list, add_messages]


class Agent:
    def __init__(self, llm, username: str):
        tools = [_create_get_basic_info(username), _create_get_dietary_info(username),
                 _create_get_available_workouts(), _create_get_available_meals()]
        self.llm = llm.bind_tools(tools)
        self.graph = self._build_graph(tools)

    def stream_graph_update(self, user_input: str, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        human_message = HumanMessage(content=user_input)
        for event in self.graph.stream({"messages": [human_message]}, config):
            for value in event.values():
                message = value["messages"][-1]
                if not isinstance(message, ToolMessage):
                    yield value["messages"][-1].content

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
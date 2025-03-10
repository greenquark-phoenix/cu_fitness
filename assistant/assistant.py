from typing import Annotated

from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


class Agent:
    def __init__(self, llm):
        self.llm = llm
        self.graph = self._build_graph()

    def stream_graph_update(self, user_input: str, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        for event in self.graph.stream({"messages": [{"role": "user", "content": user_input}]}, config):
            for value in event.values():
                yield value["messages"][-1].content

    def _build_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("llm", self._llm)
        graph_builder.add_edge(START, "llm")
        graph_builder.add_edge("llm", END)

        memory = MemorySaver()

        return graph_builder.compile(checkpointer=memory)

    def _llm(self, state: State):
        return {"messages": [self.llm.invoke(state["messages"])]}

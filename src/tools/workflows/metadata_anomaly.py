import logging
from typing import Annotated, Sequence
import operator
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import BaseMessage


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def node1(state: State) -> State:
    logging.info("Node-1 processing input")
    input1 = (
        state["messages"][-1]["content"] if state["messages"] else "No input provided"
    )
    response = {
        "role": "assistant",
        "content": str(input1) + ", From Node-1: Hello, Human",
    }
    return {"messages": [response]}


def node2(state: State) -> State:
    logging.info("Node-2 processing input")
    input2 = (
        state["messages"][-1]["content"] if state["messages"] else "No input provided"
    )
    response = {
        "role": "assistant",
        "content": str(input2) + ", From Node-2: Hello, Human and Node-1",
    }
    return {"messages": [response]}


workflow = StateGraph(State)


workflow.add_node(node="Node-1", action=node1)
workflow.add_node(node="Node-2", action=node2)
workflow.add_edge(START, "Node-1")
workflow.add_edge("Node-1", "Node-2")
workflow.add_edge("Node-2", END)

graph = workflow.compile()

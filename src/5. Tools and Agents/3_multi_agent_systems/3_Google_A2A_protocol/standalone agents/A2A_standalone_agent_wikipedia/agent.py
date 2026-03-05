from collections.abc import AsyncIterable
from typing import Any, Literal

import httpx
import tomli

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Load configuration
with open("agent_config.toml", "rb") as f:
    config = tomli.load(f)

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

memory = MemorySaver()

class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


# Get the agent class name from config
agent_name = config["agent"]["name"]

# Define the agent class with the name from config
class Agent:
    # Read system instruction from config
    SYSTEM_INSTRUCTION = config["agent"]["system_instruction"]
    # Read supported content types from config
    SUPPORTED_CONTENT_TYPES = config["agent"]["supported_content_types"]
    def __init__(self):
        # Read model configuration from config
        self.model = ChatOpenAI(
            model=config["model"]["name"], 
            temperature=config["model"]["temperature"]
        )
        self.tools = [wikipedia]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=ResponseFormat,
        )

    def invoke(self, query, sessionId) -> str:
        graph_config = {'configurable': {'thread_id': sessionId}}
        self.graph.invoke({'messages': [('user', query)]}, graph_config)
        return self.get_agent_response(graph_config)

    async def stream(self, query, sessionId) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        graph_config = {'configurable': {'thread_id': sessionId}}

        for item in self.graph.stream(inputs, graph_config, stream_mode='values'):
            message = item['messages'][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': config["streaming"]["working_messages"][0],
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': config["streaming"]["working_messages"][1],
                }

        yield self.get_agent_response(graph_config)

    def get_agent_response(self, graph_config):
        current_state = self.graph.get_state(graph_config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            if (
                structured_response.status == 'input_required'
                or structured_response.status == 'error'
            ):
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'completed':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }

        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': config["streaming"]["error_message"],
        }

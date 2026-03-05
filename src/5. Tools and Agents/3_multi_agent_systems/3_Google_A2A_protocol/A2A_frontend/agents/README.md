## Sample Agents

All the agents in this directory are samples built on different frameworks highlighting different capabilities. Each agent runs as a standalone A2A server. 

Each agent can be run as its own A2A server with the instructions on its README. By default, each will run on a separate port on localhost (you can use command line arguments to override).

To interact with the servers, use an A2AClient in a host app (such as the CLI). See [Host Apps](/samples/python/hosts/README.md) for details.

* [**LangGraph**](/samples/python/agents/langgraph/README.md)  
Sample agent which can convert currency using tools. Showcases multi-turn interactions, tool usage, and streaming updates. 

* [**Semantic Kernel Agent**](/samples/python/agents/semantickernel/README.md)  
Demonstrates how to implement a travel agent built on [Semantic Kernel](https://github.com/microsoft/semantic-kernel/) and exposed through the A2A protocol.

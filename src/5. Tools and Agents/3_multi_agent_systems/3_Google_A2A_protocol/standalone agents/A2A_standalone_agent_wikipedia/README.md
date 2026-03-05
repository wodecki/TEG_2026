# Wikipedia Search Agent

A simple Wikipedia search agent built with LangGraph, following Configuration Driven Development principles.

## Configuration

The agent is configured using `config.toml`, which contains:

- Agent name and system instructions
- Supported content types
- Model configuration (name and temperature)
- Streaming messages
- Server configuration (host and port)
- Agent card details including capabilities and skills

This configuration-driven approach makes it easy to modify the agent's behavior without changing the code.

### Configuration Sections

```toml
[agent]
# Agent name, system instructions, and supported content types

[model]
# LLM model name and temperature settings

[streaming]
# Messages displayed during streaming operations

[server]
# Default host and port settings

[agent_card]
# Agent card details, capabilities, and skills
```

## Running the Agent

To run the agent:

```bash
uv run .
```

## Development

This project follows Configuration Driven Development practices:
- Agent parameters are read from `config.toml`
- Agent card details are defined in `config.toml`
- Code is decoupled from configuration

To modify the agent's behavior, simply update the configuration file rather than changing the code directly.

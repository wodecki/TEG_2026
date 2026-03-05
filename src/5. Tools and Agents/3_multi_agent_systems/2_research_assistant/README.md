# Research Assistant

A LangGraph-based multi-agent research assistant that creates well-researched articles through a collaborative workflow of specialized AI agents.

## Overview

This application uses four specialized agents working in sequence to produce publication-quality research articles:

1. **Search Agent** - Finds relevant sources from web, Wikipedia, and arXiv
2. **Outliner Agent** - Creates structured outlines from research findings
3. **Writer Agent** - Writes comprehensive articles following the outline
4. **Editor Agent** - Provides feedback and iterative improvements (max 3 iterations)

## Quick Start

### Prerequisites

- Python 3.13+
- OpenAI API key
- Tavily API key (for web search)

### Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment variables:**
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   LANGSMITH_API_KEY=your_langsmith_key
   ```

3. **Run the application:**
   ```bash
   uv run langgraph dev
   ```

   This starts the LangGraph Studio interface at: https://smith.langchain.com/studio/

## Usage

### Sample Questions

Try these research questions to test the system:

- "What is the potential of GenAI in banking?"
- "How are large language models transforming healthcare?"
- "What are the latest developments in quantum computing applications?"
- "How is AI being used in climate change research?"

### Expected Workflow

1. **Search Phase**: Agent searches multiple sources and compiles relevant articles
2. **Outline Phase**: Creates structured outline with bullet points and sources
3. **Writing Phase**: Produces article in TITLE/BODY format
4. **Editing Phase**: Provides feedback on keywords, titles, headers, and references
5. **Iteration**: Writer revises based on feedback (up to 3 rounds)

## Architecture

### Agent Workflow
```
search → tools → search (loop until complete)
      ↓
   outliner → writer → editor → writer (max 3 iterations)
                            ↓
                           END
```

### Agent Responsibilities

- **Search Agent**: Uses Tavily, Wikipedia, and arXiv tools to find relevant sources
- **Outliner Agent**: No tools, focuses on structuring information into clear outlines
- **Writer Agent**: No tools, specializes in article composition and revision
- **Editor Agent**: No tools, provides constructive feedback following editorial guidelines

### Configuration

- **Model**: GPT-4o-mini (temperature: 0)
- **Max Iterations**: 3 editing rounds
- **Prompt Templates**: Stored in `config/prompts.toml`
- **Tools**: Tavily search (5 results), Wikipedia, arXiv

## Development

### Updating Dependencies

```bash
# Update specific packages
uv add --upgrade langgraph langgraph-cli

# Update all packages
uv sync --upgrade

# Check for outdated packages
uv pip list --outdated
```

### Modifying Agent Prompts

Edit the system messages in `config/prompts.toml`:
- `[search]` - Search strategy and formatting
- `[outliner]` - Outline structure requirements
- `[writer]` - Article format and revision handling
- `[editor]` - Editorial guidelines and completion criteria

### Testing

```bash
# Test graph compilation
uv run python -c "import agent; print('Graph compiled successfully')"

# Run with custom input (uncomment test code in agent.py)
uv run python agent.py
```

## Troubleshooting

### Common Issues

1. **Deprecation Warning**: TavilySearchResults deprecation is expected, functionality remains intact

2. **Graph Visualization**: If the writer-editor feedback loop isn't visible in LangGraph Studio:
   - Ensure you're using LangGraph 0.6.7+ and API 0.4.29+
   - The conditional edges use explicit path mapping for proper visualization

3. **API Keys**: Verify all required environment variables are set in `.env`

4. **Dependencies**: Run `uv sync` after any `pyproject.toml` changes

### Version Compatibility

- LangGraph: 0.6.7+
- LangGraph CLI: 0.4.2+
- LangGraph API: 0.4.29+
- Python: 3.13+

## Files Structure

- `agent.py` - Main application with all agents and graph definition
- `config/prompts.toml` - Agent system message templates
- `langgraph.json` - LangGraph CLI configuration
- `.env` - Environment variables (not committed)
- `pyproject.toml` - Python dependencies
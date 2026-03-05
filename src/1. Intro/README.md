# Introduction to Generative AI - Getting Started with LLMs

Welcome to your first hands-on experience with Large Language Models! This introductory module provides the foundation for understanding how LLMs work and how to interact with them programmatically.

## 🎯 Learning Objectives

By completing this module, you will:
- Understand the fundamental concepts of LLM interaction
- Learn how system prompts shape AI behavior
- Master parameter tuning (temperature, tokens, models)
- Build your first AI-powered web application
- Establish best practices for API usage and cost management

## 📚 Module Content

### 1. LLM Basics (`1_llm_basics.py`)
**🚀 Your first interactive journey with LLMs**

This comprehensive script teaches core concepts through practical examples:
- **System Prompts**: How to give AI a personality and role
- **Temperature Control**: Balancing creativity (high) vs consistency (low)
- **Token Management**: Understanding cost and response length
- **Model Selection**: Choosing the right model for your task
- **Parameter Combinations**: Advanced configurations for different use cases

**Key Learning Points:**
- Temperature: 0.0 (deterministic) to 2.0 (highly creative)
- Token limits control both cost and response quality
- System prompts are the foundation of AI behavior
- Different models have different strengths and costs

### 2. Your Own Chatbot (`2_Your_own_chatbot.py`)
**🤖 Build a complete web application**

Create a fully functional chatbot with:
- **Streamlit Web Interface**: Professional web app in minutes
- **Custom Personality**: Hip-hop academic teacher (easily customizable)
- **Session Management**: Conversation memory and context
- **Error Handling**: Proper API key validation and error messages
- **Public Deployment**: Optional public access setup

## 🚀 Quick Start

### Prerequisites
- Python 3.13 or higher
- OpenAI API key (required)
- Anthropic API key (optional for future modules)

### Setup Instructions

1. **Navigate to the module**:
   ```bash
   cd "src/1. Intro"
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Configure API keys**:
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env with your actual API keys
   # At minimum, add your OPENAI_API_KEY
   ```

4. **Verify your setup**:
   ```bash
   # Test with the basics script
   uv run python 1_llm_basics.py
   ```

### Running the Examples

#### Interactive Learning Script
```bash
# Comprehensive LLM fundamentals (recommended first step)
uv run python 1_llm_basics.py
```
This script runs multiple examples showing:
- Different system prompt styles
- Temperature effects on creativity
- Token limit demonstrations
- Cost optimization techniques

#### Web Application
```bash
# Launch the chatbot web interface
uv run streamlit run 2_Your_own_chatbot.py
```
- Open your browser to `http://localhost:8501`
- Chat with your AI assistant
- Experiment with different prompts and questions

### Optional: Public Access
For sharing your chatbot publicly:
```bash
# Install localtunnel (requires Node.js)
npm install -g localtunnel

# Run your app in one terminal
uv run streamlit run 2_Your_own_chatbot.py

# In another terminal, create public tunnel
npx localtunnel --port 8501
```

## 🛠️ Key Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| `openai` | OpenAI API integration | ≥1.0.0 |
| `anthropic` | Claude API (future modules) | ≥0.68.1 |
| `streamlit` | Web application framework | ≥1.50.0 |
| `python-dotenv` | Environment management | ≥1.0.0 |
| `langchain-openai` | LangChain integration (future) | ≥0.3.33 |
| `langchain-anthropic` | Anthropic integration (future) | ≥0.3.20 |

## 🎓 Learning Path

### Beginner (Start Here!)
1. **Read this README** - Understand the module goals
2. **Set up your environment** - API keys and dependencies
3. **Run `1_llm_basics.py`** - Interactive learning experience
4. **Try the chatbot** - See a complete application

### Hands-On Exploration
1. **Modify system prompts** - Change the AI's personality
2. **Experiment with temperature** - See creativity vs consistency
3. **Test token limits** - Understand cost implications
4. **Customize the chatbot** - Make it your own

### Advanced Experimentation
1. **Try different models** - GPT-3.5 vs GPT-4 comparison
2. **Create custom applications** - Build beyond the examples
3. **Optimize for cost** - Learn production best practices

## 💡 Practical Tips

### API Key Best Practices
- Never commit API keys to version control
- Use `.env` files for local development
- Monitor your usage on the OpenAI dashboard
- Start with smaller, cheaper models for experimentation

### Parameter Experimentation Guide
```python
# Conservative (predictable, cheaper)
temperature=0.1, max_tokens=150, model="gpt-3.5-turbo"

# Creative (varied responses, more expensive)
temperature=1.5, max_tokens=500, model="gpt-4"

# Balanced (good for most applications)
temperature=0.7, max_tokens=300, model="gpt-3.5-turbo"
```

### Common Beginner Mistakes to Avoid
- Setting temperature too high (>1.5) for factual content
- Not setting token limits (can be expensive)
- Vague system prompts (be specific about desired behavior)
- Not handling API errors in production code

## 🔧 Customization Guide

### Modifying the Chatbot Personality
In `2_Your_own_chatbot.py`, find and modify:
```python
system_prompt = """
Your custom personality here...
Be specific about:
- Tone and style
- Level of expertise
- Response format
- Special knowledge areas
"""
```

### Adding New Features
The examples are designed to be extended. Consider adding:
- Conversation memory across sessions
- Multiple AI personalities to choose from
- File upload and analysis capabilities
- Voice input/output integration

## 📈 Cost Management

### Understanding Token Usage
- **Input tokens**: Your prompt + system prompt
- **Output tokens**: The AI's response
- **Total cost**: (input tokens × input rate) + (output tokens × output rate)

### Cost Optimization Tips
1. Use shorter system prompts when possible
2. Set appropriate `max_tokens` limits
3. Start with GPT-3.5-turbo for development
4. Monitor usage in the OpenAI dashboard

### Typical Costs (as of 2024)
- GPT-3.5-turbo: ~$0.001 per 1K tokens
- GPT-4: ~$0.03 per 1K tokens
- 1K tokens ≈ 750 words of English text

## 🚀 Next Steps

After mastering this introductory module, you'll be ready to explore:

1. **Module 2 (Models)**: Advanced model integration and response analysis
2. **Module 3 (RAG)**: Retrieval Augmented Generation for knowledge-based AI
3. **Module 4 (Chains)**: Workflow automation with LangGraph
4. **Module 5 (Agents)**: Autonomous AI agents with tools
5. **Module 6 (MCP)**: Model Context Protocol for advanced integrations

## 🤝 Getting Help

### Troubleshooting Common Issues
- **API Key Error**: Ensure your `.env` file has the correct `OPENAI_API_KEY`
- **Import Error**: Run `uv sync` to install all dependencies
- **Rate Limit Error**: You're making requests too quickly; add delays
- **Insufficient Quota**: Check your OpenAI account billing and limits

### Additional Resources
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python dotenv Guide](https://github.com/theskumar/python-dotenv)

## 📝 Educational Philosophy

This module follows a **hands-on, experiment-first** approach:
- **Learn by doing**: Every concept has runnable code
- **Immediate feedback**: See results of parameter changes instantly
- **Real-world focus**: Examples you can actually use and extend
- **Progressive complexity**: From simple concepts to complete applications

Welcome to the exciting world of Generative AI! 🚀
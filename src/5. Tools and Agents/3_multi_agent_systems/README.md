# Module 3: Multi-Agent Systems

This module demonstrates advanced multi-agent architectures where specialized agents collaborate to solve complex problems. You'll learn to build supervisor-coordinated systems, sequential workflows, and Google's Agent-to-Agent (A2A) protocol implementations.

## 📚 Learning Objectives

By completing this module, you will:
- Understand multi-agent coordination patterns and supervisor architectures
- Build sequential agent workflows for complex research and content creation
- Implement Google's A2A protocol for distributed agent communication
- Design specialized agents with domain-specific expertise
- Create production-ready multi-agent systems with proper configuration management
- Master advanced LangGraph patterns for multi-agent orchestration

## 🎯 Core Examples

### `1. multi-agent-react/`
**Supervisor-Coordinated Multi-Agent System**
- **Architecture**: Single supervisor coordinating 5 specialized agents
- **Agent Types**: Math expert, internet search, Wikipedia knowledge, arXiv research, weather
- **Pattern**: Hub-and-spoke coordination with intelligent routing
- **Tools**: Tavily search, OpenWeatherMap, Wikipedia API, arXiv integration
- **Use Case**: Complex queries requiring different types of expertise

### `2_research_assistant/`
**Sequential Multi-Agent Research Workflow**
- **Architecture**: Linear pipeline of 4 specialized agents working in sequence
- **Agent Flow**: Search → Outliner → Writer → Editor (with iteration control)
- **Pattern**: Sequential handoff with state management and iteration limits
- **Configuration**: TOML-based system prompts and agent behavior
- **Use Case**: Automated research article generation with quality control

### `3_Google_A2A_protocol/`
**Google Agent-to-Agent Protocol Implementation**
- **Architecture**: Distributed agent network with standardized communication
- **Components**: Standalone agents, frontend management system, and A2A SDK
- **Pattern**: Microservices-style agent deployment with discovery and routing
- **Agent Types**: Math, Weather, Tavily search, Wikipedia, arXiv (each on separate ports)
- **Use Case**: Enterprise-scale agent orchestration and deployment

## 🚀 Getting Started

### Prerequisites
- Completion of Modules 1 and 2 or equivalent multi-tool agent experience
- Python 3.13 or higher
- OpenAI API key
- External API keys (Tavily, OpenWeatherMap) for full functionality

### Environment Setup

Each subdirectory has its own environment requirements. Choose your learning path:

#### Option 1: Supervisor Multi-Agent (Beginner)
```bash
cd "1. multi-agent-react"
uv sync
cp .env.example .env
# Add OPENAI_API_KEY, TAVILY_API_KEY, OPENWEATHERMAP_API_KEY
uv run langgraph dev
```

#### Option 2: Research Assistant (Intermediate)
```bash
cd 2_research_assistant
uv sync
cp .env.example .env
# Add OPENAI_API_KEY, TAVILY_API_KEY, LANGSMITH_API_KEY
uv run langgraph dev
```

#### Option 3: A2A Protocol (Advanced)
```bash
# Start multiple agents on different ports
cd "3_Google_A2A_protocol/standalone agents/A2A_standalone_agent_math"
uv run . --port 10000

# In separate terminals, start other agents:
# Weather: port 10001, Tavily: port 10002, etc.

# Start frontend management system
cd ../../../A2A_frontend/frontend
uv run main.py
```

## 🎯 Architecture Patterns

### Supervisor Pattern (Hub-and-Spoke)
```
                    Supervisor Agent
                          |
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    Math Agent    Search Agent    Knowledge Agent
```
- **Centralized routing** based on query analysis
- **Single point of coordination** for agent selection
- **Best for**: Mixed-domain queries requiring different expertise

### Sequential Pipeline Pattern
```
Search → Outliner → Writer → Editor → END
   ▲                           |
   └─────── Iteration Loop ────┘
```
- **Linear workflow** with defined handoff points
- **State management** through agent pipeline
- **Best for**: Multi-step processes requiring sequential refinement

### Distributed A2A Pattern
```
Frontend ←→ Agent Registry ←→ Discovery Service
             ↓
    Math:10000  Weather:10001  Search:10002
```
- **Microservices architecture** with agent discovery
- **Standardized communication** through A2A protocol
- **Best for**: Enterprise deployment and scaling

## 💡 Hands-On Exercise Ideas

### Exercise 1: Expand the Supervisor System
**Objective**: Add new specialized agents to the supervisor coordination system

**Challenge**:
- Add a translation agent using a translation API or simulation
- Create a code analysis agent for programming questions
- Implement a financial data agent for economic queries
- Test the supervisor's routing logic with mixed queries

**Skills Practiced**:
- Multi-agent coordination patterns
- Supervisor routing logic
- Domain-specific agent design
- Agent capability definition

---

### Exercise 2: Customize Research Workflow
**Objective**: Modify the research assistant pipeline for different content types

**Challenge**:
- Adapt the workflow to create technical documentation instead of articles
- Add a fact-checking agent between Writer and Editor
- Implement a citation formatter agent for academic references
- Create domain-specific prompts for medical or legal research

**Skills Practiced**:
- Sequential workflow design
- Agent prompt engineering
- State management in pipelines
- Content-specific agent specialization

---

### Exercise 3: Build A2A Agent Network
**Objective**: Create a complete A2A agent ecosystem with custom agents

**Challenge**:
- Implement a custom agent following the A2A protocol structure
- Create agent configuration files with proper capabilities definition
- Set up the frontend management system to register and discover agents
- Test inter-agent communication through the A2A network

**Skills Practiced**:
- A2A protocol implementation
- Distributed agent architecture
- Agent registration and discovery
- Protocol-compliant communication

---

### Exercise 4: Performance and Monitoring
**Objective**: Implement monitoring and optimization for multi-agent systems

**Challenge**:
- Add timing and performance metrics to agent workflows
- Implement error handling and retry logic across agent boundaries
- Create a dashboard to monitor agent usage and success rates
- Optimize agent selection algorithms based on performance data

**Skills Practiced**:
- Multi-agent system monitoring
- Performance optimization techniques
- Error handling in distributed systems
- Metrics collection and analysis

---

### Exercise 5: Domain-Specific Multi-Agent Application
**Objective**: Design a complete multi-agent system for a specific domain

**Challenge**:
- Choose a domain (e.g., legal research, medical diagnosis, financial analysis)
- Design appropriate agent specializations and tools
- Implement the coordination pattern best suited for your domain
- Create proper configuration management and deployment structure

**Skills Practiced**:
- Domain analysis and agent design
- Architecture pattern selection
- End-to-end system implementation
- Production deployment considerations

---

### Exercise 6: Hybrid Multi-Agent Architecture
**Objective**: Combine different coordination patterns in a single system

**Challenge**:
- Design a system that uses both supervisor and sequential patterns
- Create agents that can participate in multiple workflow types
- Implement dynamic routing between different coordination modes
- Handle state management across different architectural patterns

**Skills Practiced**:
- Advanced multi-agent architecture
- Pattern composition and hybrid designs
- Complex state management
- Flexible agent deployment strategies

## 🧪 Testing and Validation

### Testing Different Patterns
```bash
# Test supervisor coordination
cd "1. multi-agent-react"
uv run langgraph dev
# Query: "What's the weather in Paris and what's 15 * 8?"

# Test sequential workflow
cd 2_research_assistant
uv run langgraph dev
# Query: "What is the potential of GenAI in banking?"

# Test A2A protocol
# Run multiple agent servers, then use frontend
# Query: Test cross-agent communication
```

### Validation Checklist
- ✅ Agents coordinate properly without conflicts
- ✅ State management works across agent boundaries
- ✅ Error handling gracefully manages agent failures
- ✅ Configuration management scales to multiple agents
- ✅ Performance remains acceptable with agent overhead
- ✅ System maintains consistency across complex workflows

## 📈 Learning Path Progression

### Beginner Level
- Start with the supervisor multi-agent system
- Understand basic agent coordination and routing
- Practice with single queries requiring multiple agents
- Master the hub-and-spoke coordination pattern

### Intermediate Level
- Work with the research assistant sequential workflow
- Implement custom prompts and agent behaviors
- Understand state management in multi-agent pipelines
- Practice with complex, multi-step agent workflows

### Advanced Level
- Deploy the A2A protocol system with multiple agents
- Build custom agents following protocol specifications
- Implement production-grade error handling and monitoring
- Design enterprise-scale multi-agent architectures

## 🎓 Success Criteria

You've mastered this module when you can:
- ✅ Design and implement supervisor-coordinated agent systems
- ✅ Build sequential multi-agent workflows with proper state management
- ✅ Deploy distributed agent systems using the A2A protocol
- ✅ Create domain-specific agents with appropriate tool selection
- ✅ Handle coordination challenges in multi-agent environments
- ✅ Implement monitoring and error handling for agent systems

## 🔗 Next Steps

After mastering multi-agent systems, you'll be ready for:
- **Production Deployment**: Enterprise-scale agent orchestration
- **Advanced Patterns**: Event-driven and reactive agent systems
- **Custom Protocols**: Design your own agent communication standards
- **Industry Applications**: Domain-specific multi-agent solutions

## 💡 Key Takeaways

### Coordination Patterns
- **Supervisor Pattern**: Best for diverse query types requiring different expertise
- **Sequential Pipeline**: Ideal for complex processes requiring step-by-step refinement
- **Distributed A2A**: Suitable for enterprise deployment and microservices architecture

### Design Principles
- **Single Responsibility**: Each agent should have a clear, focused domain of expertise
- **Loose Coupling**: Agents should communicate through well-defined interfaces
- **State Management**: Maintain clear state boundaries and handoff protocols
- **Error Resilience**: Design for graceful degradation when individual agents fail

### Production Considerations
- **Configuration Management**: Use external configuration for agent behavior and routing
- **Monitoring**: Implement comprehensive logging and metrics across agent boundaries
- **Scalability**: Design coordination patterns that can handle increasing agent counts
- **Security**: Ensure proper authentication and authorization in distributed systems

### Educational Insights
- Multi-agent systems require different thinking patterns than single-agent solutions
- Coordination complexity grows significantly with agent count and interaction patterns
- Configuration-driven design becomes crucial for managing multiple agent behaviors
- Real-world multi-agent systems need sophisticated error handling and recovery mechanisms

---

**Happy Learning!** 🎉

Experiment with different coordination patterns, build your own agent specializations, and explore how multiple AI agents can collaborate to solve complex problems that would be challenging for any single agent to handle alone.
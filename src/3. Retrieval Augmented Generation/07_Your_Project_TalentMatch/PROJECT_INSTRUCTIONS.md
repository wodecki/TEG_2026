# 🎓 Capstone Project: TalentMatch AI

## What You'll Build
An AI talent matching system that demonstrates GraphRAG advantages over traditional RAG for business queries. You'll solve a real staffing company problem: intelligently matching programmers to projects.

## Learning Goals
1. Implement GraphRAG with Neo4j and LangChain
2. Build intelligent matching algorithms
3. Create business intelligence capabilities
4. Compare AI system performance

## Project Overview

### Problem
Staffing companies struggle to match programmers to projects because:
- Manual matching doesn't scale (50+ programmers, multiple RFPs)
- Complex availability (partial allocations across projects)
- Need to answer business questions like "How many Python developers are available?"

### Solution
Build a GraphRAG system that:
- Extracts knowledge from CV PDFs using LLM
- Matches programmers to RFPs with real-time availability
- Answers complex business queries impossible with traditional RAG

## Project Phases (10 weeks)

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Setup and basic data

**Tasks:**
- Setup Neo4j with Docker
- Generate realistic CV PDFs (use existing 06_GraphRAG code as starting point)
- Create 3 sample RFPs
- Build basic knowledge graph

**Deliverables:**
- Working Neo4j instance
- 30+ CV PDFs with varied skills
- CV-to-graph extraction pipeline

### Phase 2: Core Matching (Weeks 3-5)
**Goal**: Build the matching engine

**Tasks:**
- Parse RFP requirements
- Implement availability calculation with partial allocations
- Create scoring algorithm for programmer-RFP matching
- Handle dynamic project assignments

**Deliverables:**
- RFP parser
- Matching algorithm with explanations
- Real-time availability system

### Phase 3: Business Intelligence (Weeks 6-8)
**Goal**: Show GraphRAG advantages

**Tasks:**
- Build query system for business scenarios
- Create comparison with Naive RAG baseline
- Implement natural language interface
- Build simple dashboard

**Key Queries to Support:**
- "How many Python developers are available next month?"
- "Find senior developers with React AND Node.js"
- "What skills are missing for the FinTech RFP?"
- "Who worked together successfully before?"

**Deliverables:**
- Natural language query interface
- GraphRAG vs Naive RAG comparison
- Business intelligence dashboard

### Phase 4: Evaluation (Weeks 9-10)
**Goal**: Document and present

**Tasks:**
- Performance benchmarking
- Create documentation
- Record demonstration video
- Final presentation

## Success Criteria

### Minimum Requirements
- [ ] Extract knowledge graph from 30+ CVs
- [ ] Process RFPs and recommend top candidates
- [ ] Answer 10 business intelligence queries correctly
- [ ] Demonstrate GraphRAG superiority on complex queries
- [ ] Complete documentation and demo

### Advanced Features (Bonus)
- [ ] What-if scenario analysis
- [ ] Team composition optimization
- [ ] Web dashboard with visualization
- [ ] Real-time project updates

## Assessment (100 points)

| Component | Weight | Description |
|-----------|--------|-------------|
| **Technical Implementation** | 40% | Code quality, architecture, performance |
| **Graph Design** | 20% | Schema design, query efficiency |
| **Matching Algorithm** | 20% | Accuracy, sophistication, explainability |
| **Documentation** | 10% | Technical docs, user guide |
| **Presentation** | 10% | Demo, value proposition, communication |

## Business Scenarios to Solve
Your system must handle these real staffing company queries:

1. **Resource Planning**: "How many Python developers available Q2?"
2. **Skills Gap**: "What skills missing for this RFP?"
3. **Team Building**: "Best 5-person team for e-commerce project?"
4. **Availability**: "Who becomes free when current projects end?"
5. **Collaboration**: "Developers who worked together successfully?"

## Getting Started

### Use Existing Code
Start with the `06_GraphRAG` implementation as your foundation:
- CV generation: `1_generate_data.py`
- Graph building: `2_data_to_knowledge_graph.py`
- Query system: `3_query_knowledge_graph.py`
- Comparison framework: `4_naive_rag_cv.py` and `5_compare_systems.py`

### Tech Stack
- **Required**: Python, Neo4j, LangChain, OpenAI API
- **Frontend**: Streamlit (simple) or React (advanced)
- **Testing**: pytest for validation

### Extension Areas
Extend the existing implementation to handle:
- RFP document parsing
- Dynamic project assignments (YAML/JSON)
- Programmer availability calculations
- Business intelligence queries
- Team composition optimization

## Resources & Support
- **Base Code**: Everything in `06_GraphRAG folder`
- **Documentation**: Neo4j Graph Academy, LangChain docs
- **Timeline**: 10 weeks with milestone reviews

## Success Tips
1. **Start with the existing 06_GraphRAG code** - don't build from scratch
2. **Focus on the business problem** - this isn't just a technical exercise
3. **Document your advantages** - show why GraphRAG beats traditional RAG
4. **Keep it practical** - real staffing companies could use this
5. **Test thoroughly** - validate your matching accuracy

---

**Goal**: Build a professional AI system that solves real business problems while demonstrating advanced GraphRAG techniques. This will be a strong portfolio piece showing your ability to apply AI to practical challenges.
#!/usr/bin/env python3
"""
🚀 Large Language Models (LLMs) - Interactive Educational Journey
===============================================================

Welcome to your hands-on exploration of Large Language Models! This script takes you
through the fundamental concepts that make LLMs work, using practical examples that
you can run, modify, and experiment with.

🎯 What You'll Learn:
- How system prompts shape AI behavior
- The impact of temperature on creativity and consistency
- How token limits control response length and cost
- Advanced parameter combinations for different use cases
- Real-world applications and best practices

🔧 Prerequisites:
- OpenAI API key in .env file (OPENAI_API_KEY=your_key_here)
- Python 3.10+ with openai and python-dotenv packages
"""

import textwrap
from openai import OpenAI
from dotenv import load_dotenv

# Use override=True to ensure project-specific settings take precedence
load_dotenv(override=True)

# Initialize OpenAI client - this creates our connection to the LLM service
client = OpenAI()

print("\n" + "="*60)
print("EXAMPLE 1: SYSTEM PROMPTS - THE AI'S PERSONALITY")
print("="*60)

"""
System prompts are special instructions that define how an AI should behave.
Think of them as giving the AI a "role" or "character" to play.

Key principles:
• Be specific about tone, style, and expertise level
• Define the AI's role clearly (teacher, expert, assistant)
• Set expectations for response format and length
• Consider your audience (beginners vs experts)
"""

# Example 0 (starting point): A helpful assistant
system_prompt = "You are a helpful assistant who explains concepts clearly and concisely."
question = "Why is the sky blue?"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": question}
]

response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=messages
)
answer = response.choices[0].message.content.strip()
print(answer)


# Example 1: Hip-Hop Teacher

system_prompt = "You are a cool teacher who explains complex topics using hip-hop slang and rhythm. Keep it educational but fun!"
question = "Why is the sky blue?"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": question}
]

response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=messages
)
answer = response.choices[0].message.content.strip()
print(answer)

# Now, Your Turn:
# Modify the system prompt above to create your own unique AI personality!
# e.g., "pirate teacher", "corporate consultant", "kindergarten helper", etc.


print("\n" + "="*60)
print("EXAMPLE 2: TEMPERATURE - THE CREATIVITY DIAL")
print("="*60)

"""
CONCEPT: Temperature Parameter
Temperature controls how "creative" or "random" the AI's responses are.

Temperature Scale:
• 0.0-0.3: Very focused, deterministic, repeatable
• 0.5-1.0: Balanced creativity and coherence
• 1.0-2.0: Highly creative, diverse, potentially unexpected

Use cases:
• Low (0.1): Factual answers, coding, math problems
• Medium (1.0): Creative writing, brainstorming, conversations
• High (1.8): Art, poetry, very creative tasks
"""

question = "Describe a sunset in one creative sentence."
temperatures = [0.1, 1.0, 1.5]

for temp in temperatures:
    behavior = ("Focused & Predictable" if temp <= 0.3 else
               "Balanced Creativity" if temp <= 1.0 else
               "Highly Creative")

    print(f"\n🌡️ Temperature: {temp} ({behavior})")

    messages = [
        {"role": "system", "content": "You are a creative writer."},
        {"role": "user", "content": question}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=temp,
        max_completion_tokens=50
    )
    answer = response.choices[0].message.content.strip()
    print(answer)
"""
KEY INSIGHT: Temperature dramatically affects creativity vs consistency.
Choose based on your use case!

# Exercise: Run this section multiple times and observe how responses change
# Hint: High temperature responses will be different each time, low won't
"""

print("\n" + "="*60)
print("EXAMPLE 3: TOKEN MANAGEMENT - CONTROLLING LENGTH AND COST")
print("="*60)

"""
Tokens are the building blocks of LLM processing (roughly 3/4 of a word).
The max_tokens parameter limits how long responses can be.

Token Economics:
• You pay for both input AND output tokens
• Longer responses cost more money
• Token limits force the AI to be concise
• Average: 1 token ≈ 0.75 words in English

Strategic uses:
• Short limits: Force concise answers, save costs
• Medium limits: Balanced detail and cost
• Long limits: Detailed explanations, comprehensive responses
"""

question = "Explain the concept of machine learning and give practical examples."
token_limits = [30, 100, 200]

for limit in token_limits:
    expected_words = int(limit * 0.75)
    cost_level = "Low" if limit <= 50 else "Medium" if limit <= 150 else "High"

    print(f"\n📏 Max Tokens: {limit} (~{expected_words} words, {cost_level} cost)")

    messages = [
        {"role": "system", "content": "You are a helpful AI teacher."},
        {"role": "user", "content": question}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        max_completion_tokens=limit,
    )
    answer = response.choices[0].message.content.strip()
    word_count = len(answer.split())

    print(f"   Actual words: {word_count}")
    print(f"   Response: {answer}")

"""
KEY INSIGHT: Token limits are a powerful tool for controlling both cost
and response style. Lower limits force conciseness!

# Exercise: Try asking a complex question with only 20 tokens
# Hint: The AI will be forced to give a very brief, focused answer
"""

print("\n" + "="*60)
print("EXAMPLE 4: ADVANCED PARAMETER COMBINATIONS")
print("="*60)

"""
CONCEPT: Parameter Synergy
Real applications combine multiple parameters for precise control.
Each parameter affects the others, so understanding combinations is crucial.

Professional Configurations:
"""

# Real-world parameter configurations with clear use cases
configs = [
    {
        "name": "📝 Technical Documentation Writer",
        "params": {"temperature": 0.3, "max_completion_tokens": 300, "top_p": 0.8},
        "use_case": "API docs, technical guides, code explanations",
        "why": "Low temp for accuracy, focused top_p for technical precision"
    },
    {
        "name": "🎨 Creative Content Generator",
        "params": {"temperature": 1.4, "max_completion_tokens": 250, "top_p": 0.95},
        "use_case": "Marketing copy, creative writing, brainstorming",
        "why": "High temp + top_p for maximum creative diversity"
    },
    {
        "name": "💬 Customer Service Bot",
        "params": {"temperature": 0.7, "max_completion_tokens": 150, "top_p": 0.9},
        "use_case": "Help desk, FAQ responses, user support",
        "why": "Balanced creativity with consistent, helpful tone"
    }
]

test_prompt = "Explain artificial intelligence and its impact on modern society."

for config in configs:
    print(f"\n🎯 {config['name']}")
    print(f"   Use Case: {config['use_case']}")
    print(f"   Parameters: {config['params']}")
    print(f"   Why: {config['why']}")

    messages = [
        {"role": "system", "content": f"You are a {config['name'].split()[1].lower()}."},
        {"role": "user", "content": test_prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        **config['params']
    )
    answer = response.choices[0].message.content.strip()
    print(f"   Response: {answer[:150]}...")

"""
KEY INSIGHT: Professional LLM applications use carefully tuned parameter
combinations. Start with these proven configs and adjust for your needs!

# Exercise: Design parameters for a "Children's Science Tutor" bot
# Hint: Consider age-appropriate language, engagement, and educational goals
"""

print("\n" + "="*60)
print("EXAMPLE 5: REAL-WORLD APPLICATIONS")
print("="*60)

"""
🌟 PUTTING IT ALL TOGETHER: Real-World Scenarios
Now let's see how professionals combine all these concepts to build practical AI applications.
"""

applications = [
    {
        "scenario": "📧 Email Response Assistant",
        "system_prompt": "You are a professional email assistant. Write polite, clear, and action-oriented responses. Always include next steps.",
        "params": {"temperature": 0.4, "max_completion_tokens": 120},
        "input": "A customer is asking about a delayed shipment and seems frustrated.",
        "learning_point": "Consistent, professional tone with limited length"
    },
    {
        "scenario": "🎓 Personalized Learning Tutor",
        "system_prompt": "You are an encouraging math tutor for middle school students. Always ask follow-up questions to check understanding.",
        "params": {"temperature": 0.8, "max_completion_tokens": 180},
        "input": "I don't understand how to solve for x in: 2x + 5 = 13",
        "learning_point": "Educational engagement with moderate creativity"
    },
    {
        "scenario": "📊 Data Analysis Explainer",
        "system_prompt": "You are a data scientist explaining insights to business stakeholders. Use clear metrics and actionable recommendations.",
        "params": {"temperature": 0.2, "max_completion_tokens": 200},
        "input": "Our website conversion rate dropped from 3.5% to 2.1% last month.",
        "learning_point": "Factual precision with structured business communication"
    }
]

for app in applications:
    print(f"\n🔧 {app['scenario']}")
    print(f"   Learning Focus: {app['learning_point']}")
    print(f"   System Setup: {app['system_prompt']}")
    print(f"   Parameters: {app['params']}")
    print(f"   User Input: '{app['input']}'")

    messages = [
        {"role": "system", "content": app['system_prompt']},
        {"role": "user", "content": app['input']}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        **app['params']
    )
    answer = response.choices[0].message.content.strip()

    print(f"\n   🤖 AI Response:")
    print(textwrap.fill(answer, width=65, initial_indent="   ", subsequent_indent="   "))

print("""

# Exercise: Design your own application scenario
# 1. Choose a real problem you want to solve
# 2. Write a system prompt that defines the AI's role
# 3. Select parameters that match your needs
# 4. Test with example inputs

# Hint: Start with problems you face in your daily work or studies
""")

print("\n" + "="*70)
print("🎉 CONGRATULATIONS! YOU'VE MASTERED LLM BASICS")
print("="*70)

"""
🧠 WHAT YOU'VE LEARNED:

1. 🎭 SYSTEM PROMPTS are your most powerful tool
   • Define AI personality, expertise, and communication style
   • Critical for setting user expectations and response quality
   • Always be specific about role, tone, and output format

2. 🌡️ TEMPERATURE controls creativity vs consistency
   • 0.0-0.3: Factual, repeatable, focused (great for technical tasks)
   • 0.5-1.0: Balanced creativity and coherence (conversations, content)
   • 1.0-2.0: Highly creative and diverse (art, brainstorming, fiction)

3. 🔢 TOKENS manage cost, length, and focus
   • You pay for input AND output tokens
   • Lower limits force conciseness and save money
   • Higher limits allow detailed explanations

4. 🎯 TOP_P refines word choice diversity
   • Works with temperature to fine-tune creativity
   • Lower values = more focused vocabulary choices
   • Professional tip: Adjust both temperature AND top_p together

5. 🔧 PARAMETER COMBINATIONS solve real problems
   • Each use case needs its own optimal configuration
   • Start with proven professional configurations
   • Always test and iterate based on your specific needs

🚀 NEXT STEPS FOR MASTERY:

🔬 EXPERIMENT:
• Try building your own customer service bot
• Create a personalized learning assistant
• Design a creative writing collaborator

📚 LEARN MORE:
• Explore prompt engineering techniques
• Study fine-tuning for specialized tasks
• Learn about retrieval-augmented generation (RAG)

💼 APPLY IN PRACTICE:
• Identify repetitive tasks in your work that AI could help with
• Build proof-of-concept applications for your specific domain
• Share your learnings with colleagues and iterate based on feedback

Remember: The best way to master LLMs is through hands-on experimentation.
Start small, measure results, and gradually build more complex applications!
"""
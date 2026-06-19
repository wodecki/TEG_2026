#!/usr/bin/env python3
"""
Customer agent for the e-commerce MCP shop.

An LLM (Claude) plays a customer who wants to buy something. It connects to the
shop's MCP server and uses every MCP primitive:

  • RESOURCE — reads `shop://policies` once, up front, as context.
  • PROMPT   — asks the server for its `negotiation_coach` prompt template and
               folds that guidance into its own system prompt.
  • TOOLS    — in an agentic loop, it searches, inspects, negotiates, and
               (if it gets a good deal) places an order.

The shop's internal floor price and strategy are invisible to the agent — it
can only discover the limits by making offers, exactly like a real buyer.

This module exposes the CustomerAgent class plus run_scenario(); demo.py drives
a concrete scenario. Requires ANTHROPIC_API_KEY (loaded from the repo-root .env).
"""

import asyncio
import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv(override=True)

if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError(
        "ANTHROPIC_API_KEY is required. Add it to the repo-root .env file "
        "(e.g. ANTHROPIC_API_KEY=sk-ant-...)."
    )

MODEL = "claude-opus-4-8"
MAX_TURNS = 16  # safety cap on the agentic loop

# Absolute path to the server script so the agent can be launched from anywhere.
SERVER_SCRIPT = str(Path(__file__).parent / "shop_server.py")


def _mcp_tools_to_anthropic(mcp_tools) -> list[dict]:
    """Translate MCP tool definitions into Anthropic tool definitions."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema,
        }
        for tool in mcp_tools
    ]


def _text_of(content) -> str:
    """Pull plain text out of an MCP content block (resource / prompt)."""
    if isinstance(content, str):
        return content
    return getattr(content, "text", str(content))


class CustomerAgent:
    """An LLM-driven buyer that shops, negotiates, and orders over MCP."""

    def __init__(self, client: anthropic.Anthropic, session: ClientSession,
                 persona: str, goal: str):
        self.client = client
        self.session = session
        self.persona = persona
        self.goal = goal

    async def _build_system_prompt(self, coach_args: dict) -> str:
        """Compose the system prompt from a server RESOURCE and a server PROMPT."""
        # RESOURCE: read store policies straight from the shop.
        policies_res = await self.session.read_resource("shop://policies")
        policies = _text_of(policies_res.contents[0])

        # PROMPT: ask the server for its negotiation coaching template.
        coach_res = await self.session.get_prompt("negotiation_coach", coach_args)
        coaching = _text_of(coach_res.messages[0].content)

        return (
            f"{self.persona}\n\n"
            f"YOUR GOAL: {self.goal}\n\n"
            "You are interacting with a shop through tools. Use them to search "
            "for products, inspect details, negotiate the price, and place an "
            "order. You cannot see the shop's internal costs or minimum price — "
            "discover their flexibility by making offers.\n\n"
            f"--- SHOP POLICIES (from the shop) ---\n{policies}\n"
            f"--- NEGOTIATION GUIDANCE (from the shop) ---\n{coaching}\n\n"
            "Think step by step, keep messages brief, and stop once the goal is "
            "met (order placed) or you've decided to walk away."
        )

    async def run(self, coach_args: dict) -> str:
        """Run the full shop → negotiate → order loop. Returns Claude's summary."""
        tools_result = await self.session.list_tools()
        tools = _mcp_tools_to_anthropic(tools_result.tools)
        print(f"  🛠️  Tools available: {[t['name'] for t in tools]}")

        system_prompt = await self._build_system_prompt(coach_args)
        print("  📄 Loaded store policies (resource) + negotiation coaching (prompt).")

        print(f"\n  🧑 Customer goal: {self.goal}\n")
        messages = [{"role": "user", "content": "Go ahead and pursue the goal."}]

        for _ in range(MAX_TURNS):
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=system_prompt,
                tools=tools,
                messages=messages,
            )

            # Surface any narration the model wrote alongside its tool calls.
            for block in response.content:
                if block.type == "text" and block.text.strip():
                    print(f"  💭 {block.text.strip()}")

            if response.stop_reason != "tool_use":
                final = "".join(b.text for b in response.content if b.type == "text")
                return final.strip()

            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                print(f"\n  📞 {block.name}({json.dumps(block.input)})")
                result = await self.session.call_tool(block.name, block.input)
                output = result.content[0].text
                # Keep the console readable; the model still gets the full text.
                preview = output if len(output) <= 320 else output[:320] + " …"
                print(f"  ↩️  {preview}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })

            messages.append({"role": "user", "content": tool_results})

        return "⚠️  Reached the turn limit without finishing the goal."


async def run_scenario(persona: str, goal: str, coach_args: dict) -> str:
    """Spawn the shop server, run a CustomerAgent against it, return the summary."""
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "--with", "mcp>=1.2.0", SERVER_SCRIPT],
    )
    client = anthropic.Anthropic()

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            agent = CustomerAgent(client, session, persona, goal)
            return await agent.run(coach_args)


if __name__ == "__main__":
    # Minimal self-contained run; demo.py provides the richer presentation.
    summary = asyncio.run(run_scenario(
        persona="You are a procurement assistant for a small gym.",
        goal=("Buy 60 Premium Cork Yoga Mats. Your hard budget is $45 per unit. "
              "Negotiate a good price and place the order under 'Gym Co' if you "
              "land at or below budget; otherwise walk away."),
        coach_args={"product_name": "Premium Cork Yoga Mat",
                    "budget_per_unit": "45", "quantity": "60"},
    ))
    print(f"\n🤖 Agent summary:\n{summary}")

#!/usr/bin/env python3
"""
MCP + LLM Agent Demo - an LLM solves a word problem by calling math MCP tools.

The earlier demos (1. interactive, 2. CLI) call MCP tools directly with
hard-coded arguments. This demo is different: it hands the math MCP server's
tools to Claude and lets the *model* decide which tools to call, with what
arguments, and in what order, to answer a natural-language question.

The flow (a manual "agentic loop"):
    1. Connect to the math MCP server and list its tools.
    2. Translate the MCP tool schemas into Anthropic tool definitions.
    3. Ask Claude a word problem, exposing those tools.
    4. While Claude wants to use a tool: execute it via MCP, feed the result
       back, and let Claude continue.
    5. Print Claude's final answer.

Requires ANTHROPIC_API_KEY (loaded from the repo-root .env).

Usage: uv run "3.mcp_demo - LLM agent.py"
       or: python3 "3.mcp_demo - LLM agent.py"
"""

import asyncio
import json
import os

import anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# load_dotenv walks up the directory tree, so it finds the repo-root .env.
load_dotenv(override=True)

# Fail fast if the credential is missing - no fallbacks, no mock answers.
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError(
        "ANTHROPIC_API_KEY is required. Add it to the repo-root .env file "
        "(e.g. ANTHROPIC_API_KEY=sk-ant-...)."
    )

# Anthropic's most capable model. The client reads ANTHROPIC_API_KEY from the env.
MODEL = "claude-opus-4-8"

# A word problem that needs several different math tools, chained together.
# Claude has no calculator of its own here - it must use the MCP tools.
QUESTION = (
    "I need help with a calculation. Take 7 multiplied by 6, then add the "
    "factorial of 5 to that result. Finally, give me the square root of the "
    "total. Use the math tools and show me the final number."
)


def mcp_tools_to_anthropic(mcp_tools) -> list[dict]:
    """Translate MCP tool definitions into Anthropic tool definitions.

    MCP and the Anthropic API describe tools almost identically - both use a
    name, a description, and a JSON Schema for the inputs. The only real
    difference is the field name for the schema (MCP: `inputSchema`,
    Anthropic: `input_schema`).
    """
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema,
        }
        for tool in mcp_tools
    ]


async def run_agent(session: ClientSession, client: anthropic.Anthropic) -> None:
    """Let Claude answer QUESTION by calling the math MCP server's tools."""
    # Step 1: discover the tools the MCP server offers.
    tools_result = await session.list_tools()
    anthropic_tools = mcp_tools_to_anthropic(tools_result.tools)
    print(f"  🛠️  Exposing {len(anthropic_tools)} MCP tools to the LLM: "
          f"{[t['name'] for t in anthropic_tools]}")

    # Step 2: start the conversation with the user's question.
    print(f"\n  🧑  User: {QUESTION}")
    messages = [{"role": "user", "content": QUESTION}]

    # Step 3: the agentic loop. Keep going until Claude stops requesting tools.
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            tools=anthropic_tools,
            messages=messages,
        )

        # Claude is done reasoning and has a final answer for us.
        if response.stop_reason != "tool_use":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            print(f"\n  🤖 Claude: {final_text}")
            break

        # Otherwise, Claude wants to call one or more tools. Preserve its full
        # response (text + tool_use blocks) in the conversation history.
        messages.append({"role": "assistant", "content": response.content})

        # Step 4: execute each requested tool against the MCP server and
        # collect the results to send back in a single user turn.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"\n  📞 Claude calls MCP tool: {block.name}({json.dumps(block.input)})")
            mcp_result = await session.call_tool(block.name, block.input)
            output = mcp_result.content[0].text
            print(f"  ↩️  MCP returns: {output}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
            })

        messages.append({"role": "user", "content": tool_results})


async def main() -> None:
    print("🤖 MCP + LLM AGENT DEMO")
    print("=" * 45)
    print("Claude solves a word problem using the math MCP server's tools.\n")

    # The math server runs as a subprocess speaking MCP over stdio.
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "--with", "mcp>=1.2.0", "math_server/math_server.py"],
    )

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            print("  🤝 Initializing MCP connection...")
            await session.initialize()
            print("  ✅ MCP initialization complete!")

            await run_agent(session, client)

    print("\n✅ DEMO COMPLETE!")
    print("=" * 45)


if __name__ == "__main__":
    asyncio.run(main())

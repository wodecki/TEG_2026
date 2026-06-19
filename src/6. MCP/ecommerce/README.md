# E-commerce MCP Demo — an LLM agent that shops and negotiates

A self-contained demo of a mini e-commerce shop exposed over the **Model Context
Protocol (MCP)**, and an **LLM customer agent** that searches the catalog,
**negotiates the price**, and **places an order** — all by calling the shop's
MCP tools.

It is the capstone of the MCP demos in this folder:

| Demo | What it shows |
|------|---------------|
| `1.mcp_demo - interactive.py` | Calling MCP tools directly (hard-coded args) |
| `2.mcp_demo - CLI.py` | Same, as a CLI across several servers |
| `3.mcp_demo - LLM agent.py` | An **LLM** deciding which math tools to call |
| **`ecommerce/`** (this) | A full app: **tools + resources + prompts**, an LLM that **negotiates**, and a **trust boundary** between customer and company data |

## The big idea: the server is a trust boundary

The product database has two layers of columns:

- **Customer-facing** — `product_id`, `name`, `description`, `category`,
  `target_group`, `unit_price`, `stock_available`.
- **Company-internal** — `unit_cost`, `floor_price`, `max_discount_pct`,
  `negotiation_strategy`, `internal_notes`.

The MCP server reads the internal columns to decide what offers to accept, but
**never returns them**. The customer agent — and the LLM driving it — literally
cannot see the floor price or strategy. It can only *discover* the shop's
flexibility by making offers, exactly like real haggling. The demo ends by
pulling back the curtain to show the internal data the agent never saw.

## Files

| File | Role |
|------|------|
| `shop_database.py` | Creates & seeds the SQLite database (`shop.db`). Run it to (re)build the DB. |
| `shop_server.py`   | The MCP server — **tools**, **resources** (assets), **prompt** templates. |
| `customer_agent.py`| The LLM customer agent (`CustomerAgent` + `run_scenario`). |
| `demo.py`          | A runnable scenario + the "behind the scenes" internal reveal. |

## What the MCP server exposes

**Tools** (the agent calls these in a loop)
- `search_products(query, target_group)` — search the catalog (public fields only)
- `get_product_details(product_id)` — full public details for one product
- `negotiate_price(product_id, quantity, offered_unit_price)` — returns
  `accept` / `counter` / `reject` + a quoted price (floor & strategy applied
  server-side, never revealed)
- `place_order(product_id, quantity, agreed_unit_price, customer_name)` —
  validates stock and that the price meets the private minimum, then issues a
  receipt and decrements stock

**Resources** (the "assets" — read-only content addressed by URI)
- `shop://catalog` — the full public catalog (JSON)
- `shop://policies` — store policies (Markdown)
- `shop://product/{product_id}` — a single product spec sheet (templated)

**Prompts** (reusable templates the client fetches from the server)
- `negotiation_coach(product_name, budget_per_unit, quantity)` — a negotiation playbook
- `product_inquiry(need)` — drafts a buyer inquiry for a stated need

The agent uses **all three**: it reads `shop://policies` as context, asks the
server for the `negotiation_coach` prompt and folds it into its system prompt,
then drives the tools.

## How negotiation works (server-side)

For each offer, the shop computes an *effective floor* (the private
`floor_price`, with ~3% extra room on bulk orders of 50+ units):

- **offer ≥ effective floor** → `accept` (you're charged your offer, capped at list).
- **offer < effective floor** → `counter` at a price between the floor and list,
  leaning per the product's strategy:
  `firm` holds near list, `flexible` meets in the middle, `clear_stock` drops
  toward the floor to move inventory.

`place_order` independently re-checks the price against the floor, so a client
**cannot** buy below the minimum even if it tries.

## Running it

From the **`6. MCP`** directory:

```bash
# 1. (optional) build the database explicitly — demo.py also resets it
uv run "ecommerce/shop_database.py"

# 2. run the full demo (resets the DB, runs the agent, reveals internals)
uv run "ecommerce/demo.py"

# or run the bare agent scenario
uv run "ecommerce/customer_agent.py"
```

**Requirements:** `ANTHROPIC_API_KEY` in the repo-root `.env` (the agent uses
`claude-opus-4-8`). Dependencies (`anthropic`, `mcp`, `python-dotenv`) are
declared in `../pyproject.toml`; run `uv sync` if needed.

## Example output (abridged)

```
🧑 Customer goal: Buy 60 Premium Cork Yoga Mats. Hard budget $45/unit ...
📞 search_products({"query": "Premium Cork Yoga Mat"})
📞 get_product_details({"product_id": "SKU-1001"})
📞 negotiate_price({"product_id": "SKU-1001", "quantity": 60, "offered_unit_price": 38})
   ↩️  decision: accept, quoted_unit_price: 38.0
📞 place_order({... agreed_unit_price: 38, customer_name: "FitZone Studios"})
   ↩️  status: confirmed, order_id: ORD-...

🔒 BEHIND THE SCENES (invisible to the agent)
   Internal floor: $38.00 | Strategy: clear_stock | Margin/unit: $16.00 ...
```

Try editing `GOAL`/budget in `demo.py`, or negotiate a `firm` product
(e.g. `SKU-1004` Smart Fitness Tracker) to watch the shop counter instead of
accepting.

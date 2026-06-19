#!/usr/bin/env python3
"""
MCP server for a mini e-commerce shop (a small fitness-gear retailer).

This server demonstrates ALL THREE MCP primitives:

  • TOOLS      — search_products, get_product_details, negotiate_price, place_order
  • RESOURCES  — shop://catalog, shop://policies, shop://product/{id}  (the "assets")
  • PROMPTS    — negotiation_coach, product_inquiry  (reusable prompt templates)

The shop's private pricing data (cost, floor price, negotiation strategy) lives
in the database but is NEVER returned to the client. negotiate_price and
place_order read it server-side to decide what to accept — so the customer can
only discover the limits by making offers, exactly like real-world haggling.

Run as an MCP stdio server:
    uv run --with "mcp>=1.2.0" ecommerce/shop_server.py
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from shop_database import DB_PATH, init_db

# Make sure the database exists and is seeded before we start serving.
init_db()

mcp = FastMCP("ecommerce-shop")

# Columns that are safe to expose to customers. The internal columns
# (unit_cost, floor_price, max_discount_pct, negotiation_strategy,
# internal_notes) are intentionally excluded everywhere customer data leaves
# the server.
PUBLIC_COLUMNS = (
    "product_id, name, description, category, target_group, "
    "unit_price, stock_available"
)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _effective_floor(floor_price: float, quantity: int) -> float:
    """The shop gives a little extra room on bulk orders (>= 50 units)."""
    factor = 0.97 if quantity >= 50 else 1.0
    return round(floor_price * factor, 2)


# Strategy → how close the counter-offer sits to list price (vs the floor).
# Higher = holds firmer near list; lower = drops toward the floor to win volume.
_COUNTER_WEIGHT = {"firm": 0.70, "flexible": 0.40, "clear_stock": 0.12}


# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool()
def search_products(query: str = "", target_group: str = "") -> str:
    """Search the shop catalog. Returns public product info only.

    Args:
        query: keyword matched against name, description and category. Empty = all.
        target_group: optional filter on the intended audience.
    """
    sql = f"SELECT {PUBLIC_COLUMNS} FROM products WHERE 1=1"
    params: list = []
    if query:
        sql += " AND (lower(name) LIKE ? OR lower(description) LIKE ? OR lower(category) LIKE ?)"
        like = f"%{query.lower()}%"
        params += [like, like, like]
    if target_group:
        sql += " AND lower(target_group) LIKE ?"
        params.append(f"%{target_group.lower()}%")
    sql += " ORDER BY unit_price"

    with _connect() as conn:
        rows = conn.execute(sql, params).fetchall()

    products = [dict(r) for r in rows]
    return json.dumps({"count": len(products), "products": products}, indent=2)


@mcp.tool()
def get_product_details(product_id: str) -> str:
    """Get full public details for one product by its ID (e.g. 'SKU-1001')."""
    with _connect() as conn:
        row = conn.execute(
            f"SELECT {PUBLIC_COLUMNS} FROM products WHERE product_id = ?",
            (product_id,),
        ).fetchone()

    if row is None:
        return json.dumps({"error": f"No product with id '{product_id}'."})
    return json.dumps(dict(row), indent=2)


@mcp.tool()
def negotiate_price(product_id: str, quantity: int, offered_unit_price: float) -> str:
    """Make a price offer for a quantity of a product.

    The shop replies with one of:
      • accept  — your offer is good; proceed to place_order at 'quoted_unit_price'
      • counter — your offer is too low; the shop quotes 'quoted_unit_price'
      • reject  — the offer/quantity can't be fulfilled

    The shop's minimum acceptable price and negotiation style are applied
    server-side and are never revealed.

    Args:
        product_id: the product to negotiate on.
        quantity: how many units you want to buy.
        offered_unit_price: your proposed price PER UNIT.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE product_id = ?", (product_id,)
        ).fetchone()

        if row is None:
            return json.dumps({"decision": "reject",
                               "message": f"No product with id '{product_id}'."})
        if quantity <= 0:
            return json.dumps({"decision": "reject",
                               "message": "Quantity must be a positive number."})
        if quantity > row["stock_available"]:
            return json.dumps({
                "decision": "reject",
                "message": f"Only {row['stock_available']} units of "
                           f"{row['name']} are in stock.",
            })

        list_price = row["unit_price"]
        floor = _effective_floor(row["floor_price"], quantity)
        strategy = row["negotiation_strategy"]

        if offered_unit_price >= floor:
            # Acceptable. Never charge more than list price.
            quoted = round(min(offered_unit_price, list_price), 2)
            decision, message = "accept", "Deal — we accept your offer."
        else:
            # Too low: quote a counter between the floor and list price.
            weight = _COUNTER_WEIGHT.get(strategy, 0.40)
            quoted = round(floor + weight * (list_price - floor), 2)
            decision = "counter"
            message = (f"That's below what we can do. We can offer "
                       f"{quoted:.2f} per unit.")

        conn.execute(
            "INSERT INTO negotiations (product_id, quantity, offered, decision, "
            "quoted, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (product_id, quantity, offered_unit_price, decision, quoted, _now()),
        )
        conn.commit()

    return json.dumps({
        "product_id": product_id,
        "name": row["name"],
        "quantity": quantity,
        "list_unit_price": list_price,
        "your_offer": round(offered_unit_price, 2),
        "decision": decision,
        "quoted_unit_price": quoted,
        "line_total_at_quote": round(quoted * quantity, 2),
        "message": message,
    }, indent=2)


@mcp.tool()
def place_order(product_id: str, quantity: int, agreed_unit_price: float,
                customer_name: str) -> str:
    """Place an order. The shop re-validates stock and that the agreed price
    meets its (private) minimum before confirming, then issues a receipt.

    Args:
        product_id: the product to buy.
        quantity: number of units.
        agreed_unit_price: the price per unit you settled on (e.g. a quote
            returned by negotiate_price).
        customer_name: name to put on the order.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE product_id = ?", (product_id,)
        ).fetchone()

        if row is None:
            return json.dumps({"status": "error",
                               "message": f"No product with id '{product_id}'."})
        if quantity <= 0:
            return json.dumps({"status": "error",
                               "message": "Quantity must be positive."})
        if quantity > row["stock_available"]:
            return json.dumps({
                "status": "error",
                "message": f"Only {row['stock_available']} units in stock.",
            })

        floor = _effective_floor(row["floor_price"], quantity)
        if agreed_unit_price < floor:
            # The boundary the client cannot bypass: no sub-floor sales.
            return json.dumps({
                "status": "rejected",
                "message": "That price is below our minimum. Negotiate a "
                           "higher price before ordering.",
            })

        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        total = round(agreed_unit_price * quantity, 2)
        conn.execute(
            "UPDATE products SET stock_available = stock_available - ? "
            "WHERE product_id = ?",
            (quantity, product_id),
        )
        conn.execute(
            "INSERT INTO orders (order_id, product_id, quantity, unit_price, "
            "total_price, customer_name, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (order_id, product_id, quantity, round(agreed_unit_price, 2),
             total, customer_name, _now()),
        )
        conn.commit()

    return json.dumps({
        "status": "confirmed",
        "order_id": order_id,
        "product_id": product_id,
        "product_name": row["name"],
        "quantity": quantity,
        "unit_price": round(agreed_unit_price, 2),
        "total_price": total,
        "customer_name": customer_name,
        "message": f"Order {order_id} confirmed. Thank you!",
    }, indent=2)


# =============================================================================
# RESOURCES (the "assets" — read-only content the client can fetch by URI)
# =============================================================================

@mcp.resource("shop://catalog")
def catalog() -> str:
    """The full public product catalog as JSON (customer-facing fields only)."""
    with _connect() as conn:
        rows = conn.execute(
            f"SELECT {PUBLIC_COLUMNS} FROM products ORDER BY category, unit_price"
        ).fetchall()
    return json.dumps([dict(r) for r in rows], indent=2)


@mcp.resource("shop://policies")
def policies() -> str:
    """Store policies (shipping, returns, payment, bulk orders) as Markdown."""
    return (
        "# FitGear Shop — Store Policies\n\n"
        "## Payment\n"
        "- Invoiced on confirmation; net-30 for business customers.\n\n"
        "## Shipping\n"
        "- Free standard shipping on orders over $250.\n"
        "- Bulk orders (50+ units) ship on a pallet within 5 business days.\n\n"
        "## Returns\n"
        "- 30-day returns on unused items in original packaging.\n"
        "- Hygiene items (shaker bottles) are non-returnable once opened.\n\n"
        "## Pricing & negotiation\n"
        "- List prices are shown per unit. We welcome offers, especially on "
        "bulk orders — make an offer and we'll respond with our best price.\n"
    )


@mcp.resource("shop://product/{product_id}")
def product_sheet(product_id: str) -> str:
    """A single product's public spec sheet, addressed by ID."""
    with _connect() as conn:
        row = conn.execute(
            f"SELECT {PUBLIC_COLUMNS} FROM products WHERE product_id = ?",
            (product_id,),
        ).fetchone()
    if row is None:
        return f"No product with id '{product_id}'."
    p = dict(row)
    return (
        f"# {p['name']} ({p['product_id']})\n\n"
        f"{p['description']}\n\n"
        f"- Category: {p['category']}\n"
        f"- For: {p['target_group']}\n"
        f"- List price: ${p['unit_price']:.2f} / unit\n"
        f"- In stock: {p['stock_available']} units\n"
    )


# =============================================================================
# PROMPTS (reusable prompt templates the client can request from the server)
# =============================================================================

@mcp.prompt()
def negotiation_coach(product_name: str, budget_per_unit: str,
                      quantity: str) -> str:
    """Coaching guidance for negotiating a good deal on a product."""
    return (
        f"You are negotiating to buy {quantity} units of '{product_name}'. "
        f"Your maximum budget is ${budget_per_unit} per unit.\n\n"
        "Negotiation playbook:\n"
        "1. Check the list price and stock with get_product_details first.\n"
        "2. Open with an offer clearly below your budget to leave room — "
        "a larger quantity is your leverage, so mention it.\n"
        "3. If the shop counters, you can accept, or counter once or twice by "
        "nudging your offer up toward (but not over) your budget.\n"
        "4. Accept as soon as the quoted price is at or under your budget; "
        "don't haggle past a good deal.\n"
        "5. If the shop's best price stays above your budget, walk away "
        "politely and do NOT place the order.\n"
        "6. Only call place_order once you have an accepted price."
    )


@mcp.prompt()
def product_inquiry(need: str) -> str:
    """Draft a buyer inquiry describing what the customer is looking for."""
    return (
        f"I'm looking for: {need}\n\n"
        "Search the catalog for matching products, compare the options on "
        "price, suitability for my stated need, and stock, then recommend the "
        "single best fit with a one-line justification."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")

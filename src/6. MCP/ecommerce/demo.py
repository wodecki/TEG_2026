#!/usr/bin/env python3
"""
End-to-end demo: an LLM customer agent shops, negotiates, and buys over MCP.

It runs one concrete scenario against the shop's MCP server, then pulls back the
curtain: it reads the company-internal columns straight from the database to
show the floor price, strategy, and realised margin — none of which the agent
could see. That contrast is the point of the demo.

Usage (from the "6. MCP" directory):
    uv run "ecommerce/demo.py"
"""

import asyncio
import sqlite3

from customer_agent import run_scenario
from shop_database import DB_PATH, init_db

# Reset to a clean, fully-stocked database so the demo is reproducible.
init_db(reset=True)

PERSONA = (
    "You are Sam, a procurement assistant for FitZone, a boutique gym opening "
    "a new studio. You are friendly but cost-conscious."
)
GOAL = (
    "Buy 60 Premium Cork Yoga Mats for the new studio. Your hard budget is "
    "$45 per unit. Negotiate firmly but fairly to get the best price you can, "
    "then place the order under the name 'FitZone Studios' once you reach a "
    "deal at or below your budget. If the best price stays above $45, walk away."
)
COACH_ARGS = {
    "product_name": "Premium Cork Yoga Mat",
    "budget_per_unit": "45",
    "quantity": "60",
}


def reveal_internal_view() -> None:
    """Show the company-internal data the customer agent never had access to."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        order = conn.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        if order is None:
            print("\n🔒 BEHIND THE SCENES: no order was placed (agent walked away).")
            rounds = conn.execute("SELECT COUNT(*) FROM negotiations").fetchone()[0]
            print(f"   The shop logged {rounds} offer(s) during the conversation.")
            return

        product = conn.execute(
            "SELECT * FROM products WHERE product_id = ?", (order["product_id"],)
        ).fetchone()
        rounds = conn.execute(
            "SELECT COUNT(*) FROM negotiations WHERE product_id = ?",
            (order["product_id"],),
        ).fetchone()[0]

        agreed = order["unit_price"]
        margin_unit = agreed - product["unit_cost"]
        margin_total = margin_unit * order["quantity"]
        off_list = (1 - agreed / product["unit_price"]) * 100

        print("\n" + "=" * 60)
        print("🔒 BEHIND THE SCENES (company-internal — invisible to the agent)")
        print("=" * 60)
        print(f"  Product            : {product['name']}")
        print(f"  List price         : ${product['unit_price']:.2f}")
        print(f"  Internal unit cost : ${product['unit_cost']:.2f}")
        print(f"  Internal floor     : ${product['floor_price']:.2f}")
        print(f"  Strategy           : {product['negotiation_strategy']}")
        print(f"  Internal note      : {product['internal_notes']}")
        print(f"  Negotiation rounds : {rounds}")
        print("  " + "-" * 56)
        print(f"  AGREED price/unit  : ${agreed:.2f}  ({off_list:.1f}% off list)")
        print(f"  Units sold         : {order['quantity']}")
        print(f"  Margin / unit      : ${margin_unit:.2f}")
        print(f"  Total margin        : ${margin_total:,.2f}")
        print(f"  Stayed above floor : {'YES ✅' if agreed >= product['floor_price'] else 'NO ❌'}")
    finally:
        conn.close()


async def main() -> None:
    print("🛒 E-COMMERCE MCP DEMO — LLM customer agent negotiates a purchase")
    print("=" * 60)

    summary = await run_scenario(PERSONA, GOAL, COACH_ARGS)

    print("\n" + "=" * 60)
    print("🤖 AGENT'S FINAL SUMMARY")
    print("=" * 60)
    print(summary)

    reveal_internal_view()

    print("\n✅ DEMO COMPLETE!")


if __name__ == "__main__":
    asyncio.run(main())

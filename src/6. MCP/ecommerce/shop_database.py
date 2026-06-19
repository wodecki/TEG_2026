#!/usr/bin/env python3
"""
E-commerce database for the MCP shop demo (a small fitness-gear retailer).

The schema is deliberately split into two layers — this split is the whole
point of the demo:

  • CUSTOMER-FACING columns  (product_id, name, description, category,
    target_group, unit_price, stock_available) are safe to show anyone.

  • COMPANY-INTERNAL columns (unit_cost, floor_price, max_discount_pct,
    negotiation_strategy, internal_notes) are trade secrets. They drive what
    deals the shop will accept, and they must NEVER reach the customer.

The MCP server (shop_server.py) is the trust boundary: it reads the internal
columns to decide whether to accept an offer, but only ever returns the
customer-facing columns. The customer agent literally cannot see the floor
price or the negotiation strategy — it can only probe with offers.

Run this file directly to (re)create and seed the database:
    uv run ecommerce/shop_database.py
"""

import sqlite3
from pathlib import Path

# Resolve the DB path relative to THIS file so it works regardless of the
# current working directory (the MCP server is spawned from elsewhere).
DB_PATH = Path(__file__).parent / "shop.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    -- ---- customer-facing (safe to expose) ----
    product_id           TEXT PRIMARY KEY,
    name                 TEXT    NOT NULL,
    description          TEXT    NOT NULL,
    category             TEXT    NOT NULL,
    target_group         TEXT    NOT NULL,   -- who the product is for
    unit_price           REAL    NOT NULL,   -- public list price
    stock_available      INTEGER NOT NULL,
    -- ---- company-internal (trade secrets, never exposed) ----
    unit_cost            REAL    NOT NULL,   -- what the item costs us
    floor_price          REAL    NOT NULL,   -- absolute minimum unit price we accept
    max_discount_pct     REAL    NOT NULL,   -- largest % off list we will ever grant
    negotiation_strategy TEXT    NOT NULL,   -- 'firm' | 'flexible' | 'clear_stock'
    internal_notes       TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id      TEXT PRIMARY KEY,
    product_id    TEXT    NOT NULL,
    quantity      INTEGER NOT NULL,
    unit_price    REAL    NOT NULL,          -- agreed price per unit
    total_price   REAL    NOT NULL,
    customer_name TEXT    NOT NULL,
    created_at    TEXT    NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Internal log of every offer the shop received (useful sales intelligence).
CREATE TABLE IF NOT EXISTS negotiations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id   TEXT    NOT NULL,
    quantity     INTEGER NOT NULL,
    offered      REAL    NOT NULL,
    decision     TEXT    NOT NULL,           -- 'accept' | 'counter' | 'reject'
    quoted       REAL,                       -- price the shop quoted back
    created_at   TEXT    NOT NULL
);
"""

# (product_id, name, description, category, target_group, unit_price,
#  stock_available, unit_cost, floor_price, max_discount_pct,
#  negotiation_strategy, internal_notes)
PRODUCTS = [
    (
        "SKU-1001", "Premium Cork Yoga Mat",
        "Eco-friendly natural cork mat, 5mm, non-slip, with carry strap.",
        "Yoga & Mobility", "Studios & wellness enthusiasts",
        59.99, 480,
        22.00, 38.00, 40.0, "clear_stock",
        "Overstocked after Q2 reorder — move volume, discount aggressively.",
    ),
    (
        "SKU-1002", "Adjustable Dumbbell Set (2–24kg)",
        "Pair of dial-adjustable dumbbells replacing 15 sets of weights.",
        "Strength", "Home-gym builders",
        299.00, 65,
        150.00, 240.00, 20.0, "firm",
        "Best-seller, supply-constrained — hold price, small discounts only.",
    ),
    (
        "SKU-1003", "Resistance Band Kit (5-piece)",
        "Latex loop bands, light-to-heavy, with door anchor and guide.",
        "Mobility", "Beginners & travellers",
        24.99, 1200,
        6.00, 15.00, 45.0, "flexible",
        "High margin, plenty of stock — meet customers in the middle.",
    ),
    (
        "SKU-1004", "Smart Fitness Tracker Pulse",
        "Heart-rate, SpO2, sleep and GPS watch with 10-day battery.",
        "Wearables", "Tech-savvy athletes",
        129.00, 210,
        70.00, 99.00, 25.0, "firm",
        "New release — protect launch pricing this quarter.",
    ),
    (
        "SKU-1005", "High-Density Foam Roller",
        "33cm grid-textured roller for myofascial release and recovery.",
        "Recovery", "Runners & physios",
        34.99, 90,
        9.00, 19.00, 50.0, "clear_stock",
        "Discontinuing the teal colourway — clear remaining units.",
    ),
    (
        "SKU-1006", "Cast-Iron Kettlebell 16kg",
        "Powder-coated kettlebell with wide flat base and ergonomic handle.",
        "Strength", "Functional-fitness crowd",
        79.99, 140,
        38.00, 60.00, 22.0, "flexible",
        "Steady seller — modest discounts fine on bulk.",
    ),
    (
        "SKU-1007", "Protein Shaker Bottle 700ml",
        "Leak-proof shaker with stainless mixing ball and storage compartment.",
        "Accessories", "Everyone",
        14.99, 3000,
        3.00, 8.00, 50.0, "clear_stock",
        "Loss-leader / add-on item — happy to discount to win the basket.",
    ),
    (
        "SKU-1008", "Treadmill Pro X",
        "Folding treadmill, 3.5HP, 22km/h, 15% incline, with training app.",
        "Cardio", "Serious home-gym owners",
        1299.00, 18,
        720.00, 1050.00, 18.0, "firm",
        "Flagship machine — protect margin, very limited discounting.",
    ),
]

INSERT_SQL = """
INSERT INTO products (
    product_id, name, description, category, target_group, unit_price,
    stock_available, unit_cost, floor_price, max_discount_pct,
    negotiation_strategy, internal_notes
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def init_db(reset: bool = False) -> Path:
    """Create the schema and seed products if the table is empty.

    Idempotent: safe to call on every server startup. Pass reset=True to wipe
    the file first (used by the standalone setup run).
    """
    if reset and DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        (count,) = conn.execute("SELECT COUNT(*) FROM products").fetchone()
        if count == 0:
            conn.executemany(INSERT_SQL, PRODUCTS)
        conn.commit()
    finally:
        conn.close()
    return DB_PATH


if __name__ == "__main__":
    path = init_db(reset=True)
    print(f"✅ E-commerce database created and seeded at: {path}")
    print(f"   {len(PRODUCTS)} products loaded.")

import json
import os
import re

ORDERS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "orders.json")

CUSTOMER_SAFE_FIELDS = [
    "order_id",
    "membership_tier",
    "placed_at",
    "status",
    "status_updated_at",
    "shipped_at",
    "delivered_at",
    "carrier",
    "tracking_number",
    "estimated_delivery",
    "customer_safe_message",
]


def _load_orders():
    with open(ORDERS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {o["order_id"]: o for o in data["orders"]}, data.get("snapshot_at")


def normalize_order_id(raw_id):
    if not raw_id:
        return ""
    cleaned = raw_id.strip().upper()
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned


def lookup_order(order_id):
    """
    Returns ONLY the customer-safe allowlisted fields.
    customer.*, internal.*, and any other field are never read into this
    return value — not filtered out afterward, never touched at all.
    """
    orders, snapshot_at = _load_orders()
    norm_id = normalize_order_id(order_id)

    if norm_id not in orders:
        return {
            "found": False,
            "message": f"No order found matching '{order_id}'. Please double-check the order ID.",
        }

    order = orders[norm_id]

    safe = {field: order.get(field) for field in CUSTOMER_SAFE_FIELDS}
    safe["items"] = [
        {"name": i.get("name"), "quantity": i.get("quantity"), "final_sale": i.get("final_sale")}
        for i in order.get("items", [])
    ]
    safe["found"] = True
    safe["snapshot_at"] = snapshot_at

    return safe


if __name__ == "__main__":
    print(lookup_order("ord-1005"))   
    print(lookup_order("ORD-9999"))   
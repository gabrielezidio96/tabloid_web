CART_SESSION_KEY_PREFIX = "cart"
DEFAULT_VERTICAL = "supermarket"

PRICE_KEYS = ("priceRegular", "priceDiscounted", "priceApp", "priceCreditCardClub")
DEFAULT_PRICE_KEY = "priceRegular"


def _normalize_entry(entry):
    if isinstance(entry, dict):
        qty = int(entry.get("qty", 0))
        price_key = entry.get("price_key", DEFAULT_PRICE_KEY)
    else:
        qty = int(entry)
        price_key = DEFAULT_PRICE_KEY
    return {"qty": qty, "price_key": price_key}


class Cart:
    def __init__(self, session, vertical=None):
        self.session = session
        self.session_key = f"{CART_SESSION_KEY_PREFIX}:{vertical or DEFAULT_VERTICAL}"
        raw = session.setdefault(self.session_key, {})
        self._items = {k: _normalize_entry(v) for k, v in raw.items()}
        session[self.session_key] = self._items

    def _save(self):
        self.session[self.session_key] = self._items
        self.session.modified = True

    def add(self, product_id, qty=1):
        key = str(product_id)
        existing = self._items.get(key, {"qty": 0, "price_key": DEFAULT_PRICE_KEY})
        new_qty = existing["qty"] + qty
        if new_qty <= 0:
            self._items.pop(key, None)
        else:
            self._items[key] = {"qty": new_qty, "price_key": existing["price_key"]}
        self._save()

    def set_qty(self, product_id, qty):
        key = str(product_id)
        if qty <= 0:
            self._items.pop(key, None)
        else:
            existing = self._items.get(key, {"price_key": DEFAULT_PRICE_KEY})
            self._items[key] = {"qty": qty, "price_key": existing.get("price_key", DEFAULT_PRICE_KEY)}
        self._save()

    def set_price_key(self, product_id, price_key):
        key = str(product_id)
        if key not in self._items or price_key not in PRICE_KEYS:
            return
        self._items[key]["price_key"] = price_key
        self._save()

    def remove(self, product_id):
        self._items.pop(str(product_id), None)
        self._save()

    def clear(self):
        self._items.clear()
        self._save()

    def items(self):
        return dict(self._items)

    def quantities(self):
        return {k: v["qty"] for k, v in self._items.items()}

    def __len__(self):
        return sum(v["qty"] for v in self._items.values())

    def __bool__(self):
        return bool(self._items)

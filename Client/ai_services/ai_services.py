from Admin.models import Product
from Location.models import Location
from django.db.models import Q

HELPDESK_PHONE = "0778053567"


def get_ai_recommendation(payload):
    season = payload.get('season', '').lower()
    last_purchase = payload.get('last_purchase', '').lower()

    if season == 'festive' or payload.get('is_festive'):
        return {
            "title": "Festive Special",
            "message": "Celebrate the season with our exclusive Holiday Gift Basket!",
            "product_id": None,
            "category": "Groceries"
        }

    if "stand" in last_purchase:
        return {
            "title": "Home Builder's Choice",
            "message": "Since you bought a stand, check out our deals on Cement and Bricks.",
            "product_id": None,
            "category": "Building Materials"
        }

    return {
        "title": "Top Pick for You",
        "message": "Check out our latest Electronics collection.",
        "category": "Electronics"
    }


def _extract_location_term(msg):
    """Pull a place name from the message after a preposition."""
    for phrase in (" in ", " at ", " near ", " around "):
        if phrase in msg:
            after = msg.split(phrase)[-1].strip()
            # take the first 1-3 words as the place
            return " ".join(after.split()[:3])
    return None


def _search_locations(term):
    return Location.objects.filter(
        Q(city__icontains=term) |
        Q(province__icontains=term) |
        Q(location_name__icontains=term),
        is_active=True,
    ).order_by('location_name')[:5]


def _search_products_for_category(search_terms):
    """Return products whose name matches any of the given terms."""
    query = " ".join(search_terms)
    products = Product.objects.filter(name__icontains=query)[:5]
    if not products.exists() and len(search_terms) > 1:
        for term in search_terms:
            if len(term) > 2:
                products = Product.objects.filter(name__icontains=term)[:5]
                if products.exists():
                    break
    return products


def get_chat_response(message, client_name=None):
    msg = message.lower().strip()
    name_part = f", {client_name}" if client_name else ""

    # ── Greeting ──────────────────────────────────────────────────────────────
    if any(w in msg for w in ("hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy")):
        return (
            f"Hello{name_part}! 👋 I'm your shopping assistant. I can help you with:<br>"
            "• <strong>Finding a product</strong> — ask 'Where can I find cement?'<br>"
            "• <strong>Coupon redemption</strong> — ask 'Nearest location in Harare'<br>"
            "• <strong>Helpdesk</strong> — ask 'Contact' or 'Phone number'"
        )

    # ── Helpdesk / Contact ─────────────────────────────────────────────────────
    if any(w in msg for w in ("contact", "helpdesk", "help desk", "support", "phone", "number", "call", "reach", "hotline")):
        return (
            f"📞 Our helpdesk is available at <strong>{HELPDESK_PHONE}</strong>.<br>"
            "We're open <strong>Monday–Friday 8am–5pm</strong> and <strong>Saturday 8am–1pm</strong>."
        )

    # ── Coupon / Location / Redemption ─────────────────────────────────────────
    is_location_query = any(w in msg for w in ("location", "store", "redeem", "coupon", "nearest", "redemption", "where to redeem", "branch"))
    if is_location_query:
        place = _extract_location_term(msg)

        if not place:
            return "📍 Sure! Please tell me your <strong>city or area</strong> and I'll find the nearest redemption location for you."

        locations = _search_locations(place)
        if locations.exists():
            lines = [f"📍 Redemption locations near <strong>{place.title()}</strong>:"]
            for loc in locations:
                lines.append(f"• {loc.location_name} — {loc.city}, {loc.province}")
            return "<br>".join(lines)

        return (
            f"I couldn't find any active locations in <strong>{place.title()}</strong>. "
            f"Please call our helpdesk at <strong>{HELPDESK_PHONE}</strong> for assistance."
        )

    # ── Product category lookup ────────────────────────────────────────────────
    category_triggers = ("where", "category", "find", "section", "which", "what", "look for", "looking for", "search")
    is_category_query = any(w in msg for w in category_triggers)

    stop_words = {
        "do", "you", "have", "sell", "price", "of", "i", "want", "looking",
        "for", "a", "an", "the", "in", "stock", "where", "can", "find",
        "which", "what", "category", "is", "are", "section", "me", "please",
        "show", "tell", "get", "buy", "purchase", "search",
    }

    search_terms = [w for w in msg.split() if w not in stop_words and len(w) > 2]

    if is_category_query and search_terms:
        products = _search_products_for_category(search_terms)
        if products.exists():
            # Group by category
            cat_map: dict = {}
            for p in products:
                cat_map.setdefault(p.category, []).append(p.name)
            lines = ["🛍️ Here's where you can find that:"]
            for cat, names in cat_map.items():
                lines.append(f"• <strong>{', '.join(names)}</strong> → <em>{cat}</em> category")
            return "<br>".join(lines)
        return (
            f"I couldn't find a product matching <strong>'{' '.join(search_terms)}'</strong> in our catalogue. "
            "Try a different keyword, or call our helpdesk at "
            f"<strong>{HELPDESK_PHONE}</strong>."
        )

    # ── General product search ─────────────────────────────────────────────────
    if search_terms:
        products = _search_products_for_category(search_terms)
        if products.exists():
            lines = ["🛒 Here's what I found:"]
            for p in products:
                lines.append(f"• {p.name} — <strong>${p.price}</strong> <em>({p.category})</em>")
            return "<br>".join(lines)

    # ── Fallback ───────────────────────────────────────────────────────────────
    return (
        "I'm not sure about that. Here's what I can help with:<br>"
        "• <strong>Product categories</strong> — e.g. 'Where can I find tiles?'<br>"
        "• <strong>Nearest redemption location</strong> — e.g. 'Location in Bulawayo'<br>"
        f"• <strong>Helpdesk</strong> — call <strong>{HELPDESK_PHONE}</strong>"
    )


def check_fraud(payload):
    try:
        amount = float(payload.get('amount', 0) or 0)
    except Exception:
        amount = 0.0

    merchant = (payload.get('merchant_name') or '').lower()
    is_online = bool(payload.get('is_online'))

    if amount >= 10000:
        return {"decision": "BLOCKED", "score": 0.98, "reason": "Amount exceeds allowed threshold"}

    if is_online and amount >= 5000:
        return {"decision": "BLOCKED", "score": 0.85, "reason": "Large online transaction"}

    suspicious_keywords = ["fraud", "scam", "suspicious"]
    if any(k in merchant for k in suspicious_keywords):
        return {"decision": "BLOCKED", "score": 0.9, "reason": "Suspicious merchant name"}

    return {"decision": "ALLOW", "score": 0.05, "reason": "No rule matched"}

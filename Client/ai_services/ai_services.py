def get_ai_recommendation(payload):
    """
    Mock AI recommendation service.
    Analyzes user data to suggest products.
    """
    season = payload.get('season', '').lower()
    last_purchase = payload.get('last_purchase', '').lower()
    
    # Simple rule-based logic for demo purposes
    if season == 'festive' or payload.get('is_festive'):
        return {
            "title": "Festive Special",
            "message": "Celebrate the season with our exclusive Holiday Gift Basket!",
            "product_id": None, # Could link to a specific product ID if known
            "category": "Groceries"
        }
    
    if "stand" in last_purchase:
         return {
            "title": "Home Builder's Choice",
            "message": "Since you bought a stand, check out our deals on Cement and Bricks.",
            "product_id": None,
            "category": "Building Materials"
        }

    # Default recommendation
    return {
        "title": "Top Pick for You",
        "message": "Check out our latest Electronics collection.",
        "category": "Electronics"
    }

from Admin.models import Product
from Location.models import Location
from django.db.models import Q

def get_chat_response(message):
    """
    Simple rule-based chat bot response with product and location search.
    """
    msg = message.lower()
    
    # 1. Pre-defined responses
    if "hello" in msg or "hi" in msg:
        return "Hello! How can I help you today?"
        
    if "hours" in msg or "open" in msg:
        return "We are open Monday to Friday, 8am to 5pm, and Saturday 8am to 1pm."
        
    if "contact" in msg or "phone" in msg or "email" in msg:
        return "You can reach us at 012-345-6789 or support@pos-system.com."

    # 2. Location Logic
    # If user asks for nearest location/redemption but hasn't provided a place
    if ("location" in msg or "store" in msg or "redemption" in msg) and "nearest" in msg:
        if not any(place in msg for place in [" in ", " at ", " near "]):
             return "To find the nearest redemption location, could you please tell me your area of residence or district?"
    
    # If user provides an area/district (heuristic: checks for "in [place]" or just assumes unmatched input might be a place)
    # For now, let's look for "in [place]" or specific keyword matching against DB
    # or if the previous query was about location (requires state, but we are stateless for now)
    # Let's simple search if the message contains a known city/province?
    # Or better: check if message contains "in <location>"
    
    location_search_term = None
    if " in " in msg:
        parts = msg.split(" in ")
        if len(parts) > 1:
            location_search_term = parts[1].strip()
    elif len(msg.split()) <= 2: # Short message, might be just the place name after a prompt
        location_search_term = msg

    if location_search_term:
        locations = Location.objects.filter(
            Q(city__icontains=location_search_term) | 
            Q(province__icontains=location_search_term) |
            Q(location_name__icontains=location_search_term)
        )[:3]
        
        if locations.exists():
            response_lines = [f"Here are the locations in '{location_search_term}':"]
            for loc in locations:
                response_lines.append(f"- {loc.location_name} ({loc.city}, {loc.province})")
            return "<br>".join(response_lines)


    # 3. Product Search
    # Remove common stop words to find the search term
    stop_words = ["do", "you", "have", "sell", "price", "of", "i", "want", "looking", "for", "search", "a", "an", "the", "in", "stock"]
    search_terms = [word for word in msg.split() if word not in stop_words]
    
    if search_terms:
        # Try searching for the whole cleaned phrase or individual keywords
        search_query = " ".join(search_terms)
        products = Product.objects.filter(name__icontains=search_query)[:5]
        
        if not products.exists() and len(search_terms) > 1:
             # Fallback: search for just the last meaningful word (often the noun)
             products = Product.objects.filter(name__icontains=search_terms[-1])[:5]

        if products.exists():
            response_lines = ["Here is what I found:"]
            for p in products:
                # Assuming 'available' logic since no quantity field exists:
                response_lines.append(f"- {p.name}: ${p.price} (Available)") 
            return "<br>".join(response_lines)

    # 4. Fallback
    if "ciment" in msg or "cement" in msg:
        return "We have plenty of cement in stock! Check out our Building Materials category."
        
    if "product" in msg or "buy" in msg:
        return "You can browse our products by category below. Is there something specific you are looking for?"
        
    return "I'm not sure. Try asking for a specific product like 'Cement' or 'Tiles', or asking for 'nearest location'."

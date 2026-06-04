import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from Admin.models import Product, Transaction
from Client.models import Client
from Location.models import Location
from Client.ai_services.ai_services import (
    get_ai_recommendation,
    get_chat_response,
    check_fraud,
)
from .auth import require_api_key


# ── Helpers ──────────────────────────────────────────────────────────────────

def _json_body(request):
    try:
        return json.loads(request.body)
    except Exception:
        return {}


# ── Health ────────────────────────────────────────────────────────────────────

@require_api_key
@require_http_methods(["GET"])
def health(request):
    return JsonResponse({"status": "ok", "service": "ConnectZw API"})


# ── AI proxy endpoints ────────────────────────────────────────────────────────

@csrf_exempt
@require_api_key
@require_http_methods(["POST"])
def ai_recommend(request):
    """
    POST /api/v1/ai/recommend/
    Body: { user_id, season, is_festive, last_purchase, transaction_history }
    Returns: { title, message, category, product_id? }
    """
    payload = _json_body(request)
    result = get_ai_recommendation(payload)
    return JsonResponse({"status": "success", "recommendation": result})


@csrf_exempt
@require_api_key
@require_http_methods(["POST"])
def ai_chat(request):
    """
    POST /api/v1/ai/chat/
    Body: { message, client_name? }
    Returns: { reply }
    """
    payload = _json_body(request)
    message = payload.get("message", "").strip()
    if not message:
        return JsonResponse({"error": "message is required"}, status=400)
    client_name = payload.get("client_name", "")
    reply = get_chat_response(message, client_name=client_name)
    return JsonResponse({"status": "success", "reply": reply})


@csrf_exempt
@require_api_key
@require_http_methods(["POST"])
def ai_fraud_check(request):
    """
    POST /api/v1/ai/fraud-check/
    Body: { transaction_id, user_id, amount, merchant_name, is_online, merchant_mcc? }
    Returns: { decision, score, reason }
    """
    payload = _json_body(request)
    result = check_fraud(payload)
    return JsonResponse({"status": "success", **result})


# ── Data endpoints (read by the AI microservice) ──────────────────────────────

@require_api_key
@require_http_methods(["GET"])
def products_list(request):
    """
    GET /api/v1/products/
    Query params: category, dealer_id, search, limit (default 100)
    """
    qs = Product.objects.select_related("dealer").all()

    if category := request.GET.get("category", ""):
        qs = qs.filter(category__iexact=category)
    if dealer_id := request.GET.get("dealer_id", ""):
        qs = qs.filter(dealer_id=dealer_id)
    if search := request.GET.get("search", ""):
        qs = qs.filter(name__icontains=search)

    try:
        limit = min(int(request.GET.get("limit", 100)), 500)
    except ValueError:
        limit = 100

    data = [
        {
            "id": p.id,
            "name": p.name,
            "price": str(p.price),
            "category": p.category,
            "image_url": p.image.url if p.image else None,
            "dealer": {
                "id": p.dealer.id,
                "name": f"{p.dealer.firstname} {p.dealer.lastname}",
            } if p.dealer else None,
        }
        for p in qs[:limit]
    ]
    return JsonResponse({"status": "success", "count": len(data), "products": data})


@require_api_key
@require_http_methods(["GET"])
def locations_list(request):
    """
    GET /api/v1/locations/
    Query params: city, province, category
    """
    qs = Location.objects.filter(is_active=True)

    if city := request.GET.get("city", ""):
        qs = qs.filter(city__icontains=city)
    if province := request.GET.get("province", ""):
        qs = qs.filter(province__icontains=province)
    if category := request.GET.get("category", ""):
        qs = qs.filter(category__icontains=category)

    data = [
        {
            "id": loc.id,
            "name": loc.location_name,
            "city": loc.city,
            "province": loc.province,
            "category": loc.category,
            "email": loc.email_address,
        }
        for loc in qs
    ]
    return JsonResponse({"status": "success", "count": len(data), "locations": data})


@require_api_key
@require_http_methods(["GET"])
def client_history(request, client_id):
    """
    GET /api/v1/clients/<client_id>/history/
    Query params: limit (default 50), transaction_type
    """
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return JsonResponse({"error": "Client not found"}, status=404)

    qs = Transaction.objects.filter(client=client).order_by("-timestamp")

    if tx_type := request.GET.get("transaction_type", ""):
        qs = qs.filter(transaction_type=tx_type)

    try:
        limit = min(int(request.GET.get("limit", 50)), 200)
    except ValueError:
        limit = 50

    data = [
        {
            "id": tx.id,
            "type": tx.transaction_type,
            "amount": str(tx.amount),
            "category": tx.category,
            "description": tx.description,
            "timestamp": tx.timestamp.isoformat(),
        }
        for tx in qs[:limit]
    ]
    return JsonResponse({
        "status": "success",
        "client": {"id": client.id, "username": client.username},
        "count": len(data),
        "transactions": data,
    })

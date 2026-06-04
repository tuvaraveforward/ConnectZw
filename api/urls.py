from django.urls import path
from . import views

urlpatterns = [
    # ── AI proxy endpoints ──────────────────────────────────────────────────────
    # POST: { season, is_festive, last_purchase, transaction_history, user_id }
    path("v1/ai/recommend/",    views.ai_recommend,    name="api_ai_recommend"),
    # POST: { message, client_name }
    path("v1/ai/chat/",         views.ai_chat,         name="api_ai_chat"),
    # POST: { transaction_id, user_id, amount, merchant_name, is_online, ... }
    path("v1/ai/fraud-check/",  views.ai_fraud_check,  name="api_ai_fraud_check"),

    # ── Data endpoints (AI microservice reads these) ────────────────────────────
    # GET: full product catalogue
    path("v1/products/",        views.products_list,   name="api_products"),
    # GET: all active locations
    path("v1/locations/",       views.locations_list,  name="api_locations"),
    # GET: transaction history for a single client
    path("v1/clients/<int:client_id>/history/", views.client_history, name="api_client_history"),
    # GET: health / connectivity check
    path("v1/health/",          views.health,          name="api_health"),
]

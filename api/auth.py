import functools
from django.conf import settings
from django.http import JsonResponse


def require_api_key(view_func):
    """Decorator that enforces X-API-Key header authentication."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        expected = getattr(settings, "AI_API_KEY", "")
        if not expected or key != expected:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

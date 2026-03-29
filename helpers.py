import functools

from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.core.cache import cache


def login_required(function):
    @functools.wraps(function)
    def wrapper(request, *args, **kw):
        if not request.session.get("email"):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"error": "Not authenticated — please log in"}, status=401)
            return HttpResponseRedirect('/auth/')
        else:
            return function(request, *args, **kw)

    return wrapper


def rate_limit(max_calls, period_seconds):
    """
    Simple IP-based rate limiter using Django's cache.
    max_calls: maximum number of allowed calls in the window
    period_seconds: window length in seconds
    """
    def decorator(function):
        @functools.wraps(function)
        def wrapper(request, *args, **kw):
            forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if forwarded_for:
                ip = forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', 'unknown')
            cache_key = f"rl:{function.__name__}:{ip}"
            count = cache.get(cache_key, 0)
            if count >= max_calls:
                return JsonResponse(
                    {'error': 'Too many requests. Please try again later.'},
                    status=429
                )
            cache.set(cache_key, count + 1, timeout=period_seconds)
            return function(request, *args, **kw)
        return wrapper
    return decorator

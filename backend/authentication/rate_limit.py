"""
Rate limiting pour les endpoints API token (iOS).
Utilise le cache Django (locmem déjà configuré).
"""
from django.core.cache import cache
from rest_framework.exceptions import Throttled


def check_rate_limit(token_id, max_requests=10, window=60):
    """
    Vérifie la limite de requêtes : 10 requêtes par minute par token.
    Lève Throttled si la limite est dépassée.
    """
    cache_key = f'ios_rate_limit_{token_id}'
    current = cache.get(cache_key, 0)
    if current >= max_requests:
        raise Throttled(detail='Limite de requêtes atteinte (10/min).')
    cache.set(cache_key, current + 1, window)

from rest_framework.throttling import AnonRateThrottle


class RefreshScopedThrottle(AnonRateThrottle):
    scope = 'refresh_limit'

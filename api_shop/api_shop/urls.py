from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from users.views import CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/profiles/', include('profiles.urls')),
    path(
        'api/login/',
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        'api/token/refresh/',
        CustomTokenRefreshView.as_view(),
        name='token_refresh',
    ),
    path('api/categories/', include('categories.urls')),
    path('api/brands/', include('brands.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'addons.errorhandlers.handler_404'

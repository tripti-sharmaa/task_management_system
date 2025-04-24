from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuthViewSet
from api.swagger import schema_view

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger',
                                         cache_timeout=0), name='schema-swagger-ui'),
]
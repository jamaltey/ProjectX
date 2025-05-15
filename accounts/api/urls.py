from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CartViewSet, WishlistViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = router.urls
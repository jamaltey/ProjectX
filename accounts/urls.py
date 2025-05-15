from django.contrib.auth.views import LogoutView
from django.urls import path, re_path

from accounts.views import *

app_name = 'accounts'

urlpatterns = [
    path('info/', EditProfile.as_view(), name='profile-info'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('shipping-address/', AddressView.as_view(), name='address'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/detail/<int:pk>', CartDetailView.as_view(), name='cart-detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]

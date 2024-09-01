from django.urls import path, re_path
from accounts.views import *

app_name = 'accounts'

urlpatterns = [
    path('info/', EditProfile.as_view(), name='profile-info'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', register, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('wishlist/update/<int:pk>', wishlist, name='wishlist-update'),
    path('wishlist/', wishlist, name='wishlist'),
    path('orders/', orders, name='orders'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('shipping-address/', AddressView.as_view(), name='address'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/detail/<int:pk>', CartDetailView.as_view(), name='cart-detail'),
    path('cart/remove-from-cart/<int:pk>', remove_from_cart, name='cart-remove'),
    path('cart/clear/', clear_cart, name='cart-clear'),
    path('cart/change-quantity/<int:pk>/<int:quantity>/', change_quantity, name='change-quantity'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]

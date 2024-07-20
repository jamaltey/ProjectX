from django.urls import path, re_path
from accounts.views import *

app_name = 'accounts'

urlpatterns = [
    path('info/<int:pk>/', EditProfile.as_view(), name='profile-info'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', register, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('wishlist/update/<int:pk>', wishlist, name='wishlist-update'),
    path('wishlist/', wishlist, name='wishlist'),
    path('orders/', orders, name='orders'),
    path('orders/<int:pk>', order_detail, name='order-detail'),
    path('shipping-address/', address, name='address'),
    path('cart/', cart, name='cart'),
    path('cart/detail/<int:pk>', cart_detail, name='cart-detail'),
    path('cart/remove-from-cart/<int:pk>', remove_from_cart, name='cart-remove'),
    path('cart/clear/', clear_cart, name='cart-clear'),
    path('cart/change-quantity/<int:pk>/<int:quantity>/', change_quantity, name='change-quantity'),
    path('checkout/', checkout, name='checkout'),
]

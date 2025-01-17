from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from core.models import Product, Cart

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['delete'], url_path='remove', url_name='remove')
    def remove_from_cart(self, request, pk=None):
        cart = request.user.cart
        product_version = get_object_or_404(cart.products, id=pk)
        product_version.delete()
        data = {
            "is_empty": not cart.products.exists(),
            "items_count": cart.products.count(),
            "discount": cart.discount,
            "total_price": cart.total_price
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='clear', url_name='clear')
    def clear_cart(self, request):
        cart = request.user.cart
        cart.products.all().delete()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='change-quantity', url_name='change-quantity')
    def change_quantity(self, request, pk=None):
        cart = request.user.cart
        product_version = get_object_or_404(cart.products, id=pk)
        quantity = int(request.data.get('quantity'))
        if quantity > 0:
            product_version.quantity = quantity
            product_version.save()
            data = {
                "price": product_version.final_price,
                "discount": cart.discount,
                "total_price": cart.total_price
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response({"detail": "Quantity must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

class WishlistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post', 'get'], url_path='toggle/(?P<pk>\d+)', url_name='toggle')
    def toggle_wishlist(self, request, pk=None):
        user = request.user
        product = get_object_or_404(Product, id=pk)
        if product in user.favorites.all():
            user.favorites.remove(product)
            is_favorite = False
        else:
            user.favorites.add(product)
            is_favorite = True
        return Response({'is_favorite': is_favorite})

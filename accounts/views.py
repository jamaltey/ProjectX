from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, Http404, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.urls import reverse_lazy
from django.views.generic import *
from .forms import SignUpForm, LoginForm, EditProfileForm, AddressForm
from core.models import *
from core.utils import isEmpty
import re

def register(request):
    next_page = request.GET.get('next')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            Cart.objects.get_or_create(user=new_user)
            login(request, new_user)
            if not isEmpty(next_page):
                return redirect(next_page)
            return redirect('core:home')
    form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def logout_view(request: HttpRequest):
    logout(request)
    return redirect('accounts:login')

class OrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return self.request.user.orders.all()

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order-detail.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(id=self.kwargs['pk'], user=self.request.user)

class CartView(LoginRequiredMixin, DetailView):
    model = Cart
    template_name = 'cart.html'

    def get_object(self, queryset=None):
        return self.model.objects.get_or_create(user=self.request.user)[0]

class CartDetailView(LoginRequiredMixin, DetailView):
    model = ProductVersion
    template_name = 'cart-detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return self.request.user.cart.products.all()

@login_required
def remove_from_cart(request: HttpRequest, pk: int):
    cart: Cart = request.user.cart
    product_version = get_object_or_404(cart.products, id=pk)
    cart.products.remove(product_version)
    return redirect('accounts:cart')

@login_required
def clear_cart(request: HttpRequest):
    cart: Cart = request.user.cart
    cart.products.clear()
    return redirect('accounts:cart')

@login_required
def change_quantity(request: HttpRequest, pk: int, quantity: int):
    response = redirect('accounts:cart')
    if quantity <= 0:
        return response
    
    cart: Cart = request.user.cart
    product_version = get_object_or_404(cart.products, id=pk)
    product_version.quantity = quantity
    product_version.save()

    return response

class WishListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'wishlist.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return self.request.user.favorites.all()

class AddressView(LoginRequiredMixin, CreateView, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'address.html'
    success_url = reverse_lazy('accounts:address')

    def get_object(self, queryset=None):
        user: User = self.request.user
        user_has_address = Address.objects.filter(user=user).exists()

        return user.address if user_has_address else None
    
    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user
        address.save()
        return redirect(self.success_url)

class CheckoutView(AddressView):
    template_name = 'checkout.html'
    success_url = reverse_lazy('accounts:orders')

    def form_valid(self, form):
        response = super().form_valid(form)
        user: User = self.request.user
        cart: Cart = user.cart

        address = self.get_object()
        order = Order.objects.create(user=user, address=address)
        order.products.set(cart.products.all())
        order.save()

        cart.clear_cart()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user: User = self.request.user
        cart: Cart = user.cart
        context.update({
            'shipping_price': Order.SHIPPING_PRICE,
            'total_price': cart.total_price + Order.SHIPPING_PRICE,
        })
        return context

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('core:home') 

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super(CustomLoginView, self).dispatch(request, *args, **kwargs)

class EditProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'profile-info.html'
    success_url = reverse_lazy('accounts:profile-info')

    def get_object(self, queryset=None):
        return self.request.user

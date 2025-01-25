from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import *
from .mixins import RedirectAuthenticatedMixin
from .forms import SignUpForm, LoginForm, EditProfileForm, AddressForm
from core.models import *

class CustomLoginView(RedirectAuthenticatedMixin, LoginView):
    form_class = LoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('core:home') 

class SignUpView(RedirectAuthenticatedMixin, CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object) # Login the user
        Cart.objects.get_or_create(user=self.object) # Create a cart for the user
        return redirect(self.get_success_url())

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
        return self.request.user.orders.get(id=self.kwargs['pk'])

class CartView(LoginRequiredMixin, DetailView):
    model = Cart
    template_name = 'cart.html'

    def get_object(self, queryset=None):
        return self.request.user.cart

class CartDetailView(LoginRequiredMixin, DetailView):
    model = ProductVersion
    template_name = 'cart-detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return self.request.user.cart.products.all()

class WishlistView(LoginRequiredMixin, ListView):
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
        return user.address if hasattr(user, 'address') else None

    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user
        address.save()
        return redirect(self.success_url)

class CheckoutView(AddressView):
    template_name = 'checkout.html'
    success_url = reverse_lazy('accounts:orders')

    def form_valid(self, form):
        super().form_valid(form)

        user: User = self.request.user
        cart: Cart = user.cart

        address = self.get_object()
        order = user.orders.create(address=address)
        for i in cart.products.all():
            order.products.add(i)
            i.product.sales += 1
            print(i.product.sales)
        order.save()

        cart.products.clear()

        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart: Cart = self.request.user.cart
        context.update({
            'shipping_price': Order.SHIPPING_PRICE,
            'total_price': cart.total_price + Order.SHIPPING_PRICE,
        })
        return context

class EditProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'profile-info.html'
    success_url = reverse_lazy('accounts:profile-info')

    def get_object(self, queryset=None):
        return self.request.user

from django.shortcuts import render, redirect, resolve_url
from django.http import HttpRequest, Http404, HttpResponse, JsonResponse
from django.contrib.auth.views import LoginView, RedirectURLMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import *
from accounts.models import User
from accounts.forms import SignUpForm, LoginForm, EditProfileForm, AddressForm
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth import logout, login, authenticate
from core.models import Product, Favorite, ProductVersion, Cart, Address, Order
from core.views import isEmpty
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

@login_required
def orders(request: HttpRequest):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, 'orders.html', context)

@login_required
def order_detail(request: HttpRequest, pk: int):
    order = Order.objects.get(id=pk, user=request.user)
    context = {
        'order': order
    }
    return render(request, 'order-detail.html', context)

@login_required
def address(request: HttpRequest):
    user = request.user
    user_has_address = Address.objects.filter(user=user).exists()

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            if user_has_address:
                address: Address = user.address
                address.address = form.cleaned_data['address']
                address.house = form.cleaned_data['house']
                address.instructions = form.cleaned_data['instructions']
                address.save()
            else:
                address = form.save(commit=False)
                address.user = user
                address.save()
            return redirect('accounts:address')
    form = AddressForm()
    if user_has_address:
        form['address'].initial = user.address.address
        form['house'].initial = user.address.house
        form['instructions'].initial = user.address.instructions

    context = {
        'form': form
    }
    return render(request, 'address.html', context)

@login_required
def cart(request: HttpRequest):
    favorites = [i.product for i in Favorite.objects.filter(user=request.user)]
    cart = Cart.objects.get_or_create(user=request.user)[0]

    context = {
        'favorites': favorites,
        'cart': cart
    }
    return render(request, 'cart.html', context)

@login_required
def cart_detail(request: HttpRequest, pk: int):
    try:
        product = request.user.cart.products.get(id=pk)
    except ObjectDoesNotExist:
        raise Http404('Product not found')
    
    context = {
        'product': product
    }
    return render(request, 'cart-detail.html', context)

@login_required
def remove_from_cart(request: HttpRequest, pk: int):
    try:
        cart: Cart = request.user.cart
        product_version = cart.products.get(id=pk)
        cart.products.remove(product_version)
    except ObjectDoesNotExist:
        raise Http404('Product not found')
    
    return redirect('accounts:cart')

@login_required
def clear_cart(request: HttpRequest):
    cart: Cart = request.user.cart
    cart.products.clear()
    return redirect('accounts:cart')

@login_required
def change_quantity(request: HttpRequest, pk: int, quantity: int):
    try:
        cart: Cart = request.user.cart
        product_version = cart.products.get(id=pk)
        if quantity > 0:
            product_version.quantity = quantity
            product_version.save()
    except ObjectDoesNotExist:
        raise Http404('Product not found')
    
    return redirect('accounts:cart')

@login_required
def wishlist(request: HttpRequest, pk: int = None):
    if pk:
        product = Product.objects.get(id=pk)
        favorite = Favorite.objects.filter(user=request.user, product=product)
        if favorite.exists():
            favorite.delete()
        else:
            Favorite.objects.create(user=request.user, product=product)

        redirect_to = re.search(r'redirect_to=(.*)', request.get_full_path())

        if redirect_to:
            redirect_to = redirect_to.group(1)
            return redirect(redirect_to)

    context = {
        'favorites': Favorite.objects.filter(user=request.user)
    }
    return render(request, 'wishlist.html', context)

@login_required
def checkout(request: HttpRequest):
    user = request.user
    cart: Cart = user.cart
    user_has_address = Address.objects.filter(user=user).exists()
    if not cart:
        return redirect('accounts:cart')

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            if user_has_address:
                address: Address = user.address
                address.address = form.cleaned_data['address']
                address.house = form.cleaned_data['house']
                address.instructions = form.cleaned_data['instructions']
                address.save()
            else:
                address = form.save(commit=False)
                address.user = user
                address.save()

            order = Order.objects.create(user=user, address=address)
            order.products.set(cart.products.all())
            order.save()
            cart.clear_cart()
            return redirect('accounts:orders')
    
    form = AddressForm()
    if user_has_address:
        form['address'].initial = user.address.address
        form['house'].initial = user.address.house
        form['instructions'].initial = user.address.instructions

    SHIPPING_PRICE = 9.99
    context = {
        'shipping_price': SHIPPING_PRICE,
        'total_price': cart.total_price + SHIPPING_PRICE,
        'user_has_address': user_has_address,
        'form': form
    }
    return render(request, 'checkout.html', context)

class UpdateAddress(UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'address.html'

    def get_success_url(self):
        return reverse_lazy(f'accounts:address')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.get_full_path()}')
        if self.request.user.id != self.get_object().user.id:
            raise PermissionDenied
        return super(UpdateAddress, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user
        address.save()
        return redirect('accounts:address')

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('core:home') 

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super(CustomLoginView, self).dispatch(request, *args, **kwargs)

class EditProfile(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'profile-info.html'

    def get_success_url(self):
        return reverse_lazy(f'core:home')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.get_full_path()}')
        if self.request.user.id != self.get_object().id:
            raise PermissionDenied
        return super(EditProfile, self).dispatch(request, *args, **kwargs)

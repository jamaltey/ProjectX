from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import *
from accounts.models import *
from .models import *
from .utils import *
from django.views.generic import *
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db.models import Q

class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user: User = self.request.user
        products = Product.objects.order_by('-id')
        newproducts = products[:4]
        bestsellers = sorted(products, key=lambda x: x.calculate_rating(), reverse=True)[:4]

        if user.is_authenticated:
            favorites = user.favorites.all()
        else:
            favorites = []

        context['newproducts'] = newproducts
        context['bestsellers'] = bestsellers
        context['favorites'] = favorites
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'colors': self.object.colors.all(),
            'storages': self.object.storages.all(),
            'comments': self.object.comments.all(),
        })

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')

        # Add to cart
        product = self.get_object()
        quantity = int(request.POST.get('quantity', 1))
        color = None ; storage = None

        if product.colors.exists():
            color = request.POST.get('color')
            if color:
                color = product.colors.get(color_name=color, product=product)

        if product.storages.exists():
            storage = request.POST.get('storage')
            if storage:
                storage = int(storage)
                storage = product.storages.get(storage=storage)

        cart = Cart.objects.get_or_create(user=request.user)[0]
        product_version, created = cart.products.get_or_create( product=product, color=color, storage=storage )

        ProductVersion.delete_empty()

        if not created:
            product_version.quantity += quantity
        else:
            product_version.quantity = quantity

        product_version.save()
        cart.save()

        return redirect('accounts:cart')


def list(request: HttpRequest, sales=False):
    products = Product.objects.order_by('-id')
    filters = ('brand', 'type', 'category')

    if request.GET:
        for key, value in request.GET.items():
            if key in filters and not isEmpty(value):
                products = [i for i in products if str(getattr(i, key)).lower() == value.lower()]

    args = QueryDict(request.GET.urlencode(), mutable=True)
    if 'sort' in args:
        args.pop('sort')
    args = args.urlencode()

    if sales:
        products = [i for i in products if i.old_price is not None]

    success = True
    search = request.GET.get('search')
    if isEmpty(search) or search == "None": search = None
    if search is not None:
        search = search.lower()
        products = [i for i in products if search in str(i).lower()+i.description.lower()]

    sort = 'Newest'

    if not products:
        success = False
    else:
        if request.GET.get('sort') == 'price-asc':
            sort = 'Cheapest'
            products = sorted(products, key=lambda i: i.price)
        elif request.GET.get('sort') == 'price-desc':
            sort = 'Most Expensive'
            products = sorted(products, key=lambda i: i.price, reverse=True)

    paginator = Paginator(products, 16)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    user: User = request.user
    if user.is_authenticated:
        favorites = user.favorites.all()
    else:
        favorites = []

    types = ProductType.objects.all()
    categories = ProductType.objects.values_list('category', flat=True).distinct()

    context = {
        'products': products, 'page': page,
        'paginator': paginator, 'search': search,
        'success': success, 'brands': Brand.objects.all(),
        'types': types, 'sort': sort, 'args': args,
        'favorites': favorites, 'categories': categories,
    }
    return render(request, 'list.html', context)

# class ProductListView(ListView):
#     model = Product
#     template_name = 'list.html'
#     context_object_name = 'products'
#     paginate_by = 16

#     def get_queryset(self):
#         products = Product.objects.order_by('-id')
#         filters = ('brand', 'type', 'category')

#         if self.request.GET:
#             for key, value in self.request.GET.items():
#                 if key in filters and not isEmpty(value):
#                     products = [i for i in products if str(getattr(i, key)).lower() == value.lower()]

#         search = self.request.GET.get('search')
#         if isEmpty(search) or search == "None": search = None
#         if search is not None:
#             search = search.lower()
#             products = [i for i in products if search in str(i).lower()+i.description.lower()]

#         return products

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         user: User = self.request.user
#         favorites = user.favorite_products if user.is_authenticated else []

#         args = QueryDict(self.request.GET.urlencode(), mutable=True)
#         if 'sort' in args:
#             args.pop('sort')
#         args = args.urlencode()

#         types = ProductType.objects.all()
#         categories = ProductType.objects.values_list('category', flat=True).distinct()

#         context.update({
#             'brands': Brand.objects.all(),
#             'types': types,
#             'favorites': favorites,
#             'categories': categories,
#         })

#         return context


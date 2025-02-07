from django.shortcuts import redirect
from django.http import *
from django.db.models import Q
from accounts.models import Cart
from .models import Product, Brand
from django.views.generic import TemplateView, DetailView, ListView

class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.order_by('-id')
        newproducts = products[:4]
        bestsellers = sorted(products, key=lambda x: x.calculate_rating(), reverse=True)[:4]

        context.update({
            'newproducts': newproducts,
            'bestsellers': bestsellers
        })
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'images': self.object.images.order_by('color__name'),
            'colors': self.object.colors.all(),
            'storages': self.object.storages.all(),
            'comments': self.object.comments.all(),
        })

        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')

        # Add to cart
        product = self.get_object()
        quantity = int(request.POST.get('quantity', 1))
        color = None ; storage = None

        if product.colors.exists():
            color = request.POST.get('color')
            if color:
                color = product.colors.get(name=color)

        if product.storages.exists():
            storage = request.POST.get('storage')
            if storage:
                storage = int(storage)
                storage = product.storages.get(storage=storage)

        cart = Cart.objects.get_or_create(user=user)[0]
        product_version, created = cart.products.get_or_create(product=product, color=color, storage=storage)

        if not created:
            product_version.quantity += quantity
        else:
            product_version.quantity = quantity

        product_version.save()
        cart.save()

        return redirect('accounts:cart')

class ProductListView(ListView):
    model = Product
    template_name = 'list.html'
    context_object_name = 'products'
    paginate_by = 8
    filters = ('brand')

    def get_queryset(self):
        products = Product.objects.all()

        search = self.request.GET.get('search')
        if search and not search.isspace():
            search = search.strip()
            products = products.filter(
                Q(title__icontains=search) | Q(brand__title__icontains=search)
            )

        category = self.kwargs.get('category')
        if category:
            category = category.lower().capitalize()
            if category == 'Sales':
                products = products.filter(old_price__isnull=False)
            else:
                products = products.filter(category__title__iexact=category)

        for key, value in self.request.GET.lists():
            if key in self.filters and value:
                products = products.filter(**{f"{key}__title__in": value})

        sort = self.request.GET.get('sort')
        if sort == 'price-asc':
            products = products.order_by('price')
        elif sort == 'price-desc':
            products = products.order_by('-price')

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        args = QueryDict(self.request.GET.urlencode(), mutable=True)
        args.pop('sort', None)
        args.pop('page', None)
        args = args.urlencode()

        sort = self.request.GET.get('sort')
        if sort == 'price-asc':
            context['sort'] = 'Cheapest'
        elif sort == 'price-desc':
            context['sort'] = 'Most expensive'

        context.update({
            'search': self.request.GET.get('search'),
            'category': self.kwargs.get('category', ''),
            'brandlist': self.request.GET.getlist('brand'),
            'brands': Brand.objects.all(),
            'args': args,
            'page': context.get('page_obj'),
        })

        return context

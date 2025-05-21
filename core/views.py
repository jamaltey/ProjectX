from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, TemplateView

from accounts.models import Cart

from .models import Brand, Product


class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        newproducts = products[:4]
        bestsellers = products.order_by('-sold_units')[:4]

        context.update({
            'newproducts': newproducts,
            'bestsellers': bestsellers
        })
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'detail.html'

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related('brand', 'specifications')
            .prefetch_related('colors')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'images': self.object.images.select_related('color').order_by('color__name'),
            'colors': self.object.colors.all(),
            'storages': self.object.storages.all(),
            'comments': self.object.comments.select_related('author'),
        })

        return context

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')

        # Add to cart
        product = self.get_object()
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        color = None
        storage = None

        if product.colors.exists():
            color_name = request.POST.get('color')
            if color_name:
                color = product.colors.get(name=color_name)

        if product.storages.exists():
            storage_val = request.POST.get('storage')
            if storage_val:
                storage_val = int(storage_val)
                storage = product.storages.get(storage=storage_val)

        cart = Cart.objects.get_or_create(user=user)[0]
        product_variant, created = cart.products.get_or_create(product=product, color=color, storage=storage)

        if not created:
            product_variant.quantity += quantity
        else:
            product_variant.quantity = quantity

        product_variant.save()
        cart.save()

        return redirect('accounts:cart')

class ProductListView(ListView):
    model = Product
    template_name = 'list.html'
    context_object_name = 'products'
    paginate_by = 8
    filters = ('brand',)

    def get_queryset(self):
        products = Product.objects.all()

        search = self.request.GET.get('search')
        if search and not search.isspace():
            search = search.strip()
            products = products.filter(
                Q(name__icontains=search) | Q(brand__name__icontains=search)
            )

        category = self.kwargs.get('category')
        if category:
            category = category.lower()
            if category == 'sales':
                products = products.filter(old_price__isnull=False)
            else:
                products = products.filter(category__name__iexact=category)

        for key, value in self.request.GET.lists():
            if key in self.filters and value:
                products = products.filter(**{f'{key}__name__in': value})

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
            'brand_list': self.request.GET.getlist('brand'),
            'brands': Brand.objects.all(),
            'args': args,
            'page': context.get('page_obj'),
        })

        return context

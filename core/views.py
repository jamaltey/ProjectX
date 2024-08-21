from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import *
from core.models import *
from django.views.generic import *
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db.models.query import QuerySet

isEmpty = lambda string: all(char in ' \t\n\r\v\f' for char in str(string)) or not string or string == 'None'

#Views
def home(request: HttpRequest):
    newproducts = Product.objects.order_by('-id')[:4]
    bestsellers = sorted(newproducts, key=lambda x: x.calculate_rating(), reverse=True)

    if request.user.is_authenticated:
        favorites = [i.product for i in Favorite.objects.filter(user=request.user)]
    else:
        favorites = []

    context = {
        'newproducts': newproducts,
        'bestsellers': bestsellers,
        'favorites': favorites
    }
    return render(request, 'index.html', context)

def delete_comment(request: HttpRequest, pk: int):
    try:
        comment = Comment.objects.get(id=pk)
    except ObjectDoesNotExist:
        return redirect('core:home')
    if not request.user == comment.author:
        raise PermissionDenied
    comment.delete()
    return redirect(f'/detail/{comment.product.id}#comment-part')

def detail(request: HttpRequest, pk: int):
    try:
        product = Product.objects.get(id=pk)
    except ObjectDoesNotExist:
        raise Http404
    
    avg_rating = product.calculate_rating()
    product.rating = Rating.objects.get_or_create(rating=avg_rating)[0]

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next=/detail/{pk}')

        # add product to cart
        product_id = request.POST.get('product_id')
        if not isEmpty(product_id):
            product_id = int(product_id)
            product = Product.objects.get(id=product_id)
            quantity = int(request.POST.get('quantity'))
            color = None ; storage = None

            if product.colors.count():
                color = request.POST.get('color')
                if not isEmpty(color):
                    color = Color.objects.get(color_name=color, product=product)

            if product.storages.count():
                storage = request.POST.get('storage')
                if not isEmpty(storage):
                    storage = int(storage)
                    storage = product.storages.get(storage=storage)

            cart = Cart.objects.get_or_create(user=request.user)[0]
            product_version, created = cart.products.get_or_create( product=product )

            ProductVersion.delete_empty()

            if color:
                product_version.color = color
            if storage:
                product_version.storage = storage

            if not created:
                product_version.quantity += quantity
            else:
                product_version.quantity = quantity

            product_version.save()
            cart.save()

            return redirect('accounts:cart')

        # add comment
        comment_text = request.POST.get('text')
        rating = request.POST.get('comment-rating')
        if not isEmpty(comment_text) and rating.isdigit():
            rating = Rating.objects.get_or_create(rating=int(rating))[0]
            comment = Comment(author=request.user, text=comment_text, product=product, rating=rating)
            comment.save()
            return redirect(f'/detail/{pk}#comment-part')

    comments = product.comments.all()
    
    if comments:
        comments = sorted(comments, key=lambda x: x.rating.rating, reverse=True)

    if request.user.is_authenticated:
        favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    else:
        favorite = False

    images = product.images.order_by('color__color_name')
    colors = product.colors.order_by('color_name')
    storages = product.storages.order_by('storage')

    context = {
        'product': product,
        'images': images, 'colors': colors,
        'storages': storages,
        'comments': comments, 'favorite': favorite
    }
    return render(request, 'detail.html', context)

def list(request: HttpRequest, sales=False):
    products = Product.objects.order_by('-id')
    filters = ('brand', 'type', 'category')

    if request.GET:
        for key, value in request.GET.items():
            if key in filters and not isEmpty(value):
                products = [i for i in products if str(eval(f'i.{key}')).lower() == value.lower()]

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

    if request.user.is_authenticated:
        favorites = [i.product for i in Favorite.objects.filter(user=request.user)]
    else:
        favorites = []

    types = ProductType.objects.all()
    categories = set([i.category for i in types])
    class x: 
        def __init__(self, set):
            self.count = len(set)
            self.set = set
        def __iter__(self):
            return iter(self.set)
    categories = x(categories) 

    context = {
        'products': products, 'page': page, 'args': args,
        'paginator': paginator, 'search': search,
        'success': success, 'brands': Brand.objects.all(),
        'types': types, 'sort': sort, 'categories': categories,
        'tab': request.GET.get('type'), 'favorites': favorites
    }
    return render(request, 'list.html', context)


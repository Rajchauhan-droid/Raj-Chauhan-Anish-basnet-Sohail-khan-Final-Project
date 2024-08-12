
# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category, Sub_Category
from brand.models import Brand
from carts.models import CartItem
from django.db.models import Q

from carts.utils import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
import datetime
from .forms import PriceRangeForm
from wishlist.models import Wishlist
from django.utils import timezone
from django.http import HttpResponseServerError

from .forms import PriceRangeForm


# store/views.py

from django.shortcuts import render, get_object_or_404
from .models import Product, Brand
from .forms import PriceRangeForm
from django.core.paginator import Paginator

def store(request, category_slug=None, brand_slug=None, sub_category_slug=None):
    products = Product.objects.all().filter(is_available=True).order_by('id')
    product_count = products.count()
    price_form = PriceRangeForm(request.GET)
    all_brands = Brand.objects.filter(product__is_available=True).distinct()

    if brand_slug:
        brand_instance = get_object_or_404(Brand, brandslug=brand_slug)
        products = products.filter(brand=brand_instance)
        product_count = products.count()

    if price_form.is_valid():
        min_price = price_form.cleaned_data['min_price']
        max_price = price_form.cleaned_data['max_price']
        if min_price:
            products = products.filter(Discount_price__gte=min_price)
        if max_price:
            products = products.filter(Discount_price__lte=max_price)

    paginator = Paginator(products, 4)  # Show 4 products per page
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)

    context = {
        'products': paged_products,
        'product_count': product_count,
        'price_form': price_form,
        'all_brands': all_brands,
    }
    return render(request, 'store/store.html', context)

from django.http import HttpResponseServerError


# views.py



def product_detail(request, category_slug, product_slug):
    try:
        single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

        orderproduct = None
        if request.user.is_authenticated:
            orderproduct = OrderProduct.objects.filter(user=request.user, product=single_product).exists()

        reviews = ReviewRating.objects.filter(product=single_product, status=True)
        related_products = single_product.related_products.all()
        product_gallery = ProductGallery.objects.filter(product=single_product)

        
        context = {
            'single_product': single_product,
            'in_cart': in_cart,
            'orderproduct': orderproduct,
            'reviews': reviews,
            'product_gallery': product_gallery,
            'related_products': related_products,
        }

        # Handle adding product to wishlist
        if request.method == 'POST' and request.user.is_authenticated:
            user_wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            user_wishlist.products.add(single_product)

        return render(request, 'store/product_detail.html', context)

    except Product.DoesNotExist:
        return HttpResponseServerError("Product not found.")






def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
            context = {
                'products':products,
                'product_count':product_count,
            }

    return render(request, 'store/store.html',context)



def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            


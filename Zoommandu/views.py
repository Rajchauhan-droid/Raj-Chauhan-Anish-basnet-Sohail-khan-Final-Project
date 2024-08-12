from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from django.core.paginator import Paginator
from store.models import Product, Category, Sub_Category
from carousels.models import Carousel
from brand.models import Brand
from django.db.models import Count

def home(request):
    # Fetch products
    products_list = Product.objects.all().filter(is_available=True).order_by('created_date')
    paginator = Paginator(products_list, 4)  # shows only  4 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    # Fetch carousel items
    carousel_list = Carousel.objects.all().order_by('-id')

    # Fetch brands
    all_brands = Brand.objects.annotate(product_count=Count('product')).distinct()

    # Fetch categories and subcategories
    categories = Category.objects.all()
    sub_categories = Sub_Category.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_html = render_to_string('product_list.html', {'products': products})
        pagination_html = render_to_string('pagination.html', {'products': products})
        return JsonResponse({
            'products_html': products_html,
            'pagination_html': pagination_html
        })

    context = {
        'products': products,
        'carousel_list': carousel_list,
        'all_brands': all_brands,
        'paginator': paginator,
        'links': categories,
        'sub_links': sub_categories,
    }
    return render(request, 'home.html', context)

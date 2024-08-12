
from .models import Category, Sub_Category

def menu_links(request):
    links = Category.objects.all()
    sub_links = Sub_Category.objects.all()
    return dict(links=links, sub_links=sub_links)
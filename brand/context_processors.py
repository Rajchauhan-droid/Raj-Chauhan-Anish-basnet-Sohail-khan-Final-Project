
from .models import Brand

def menu_links(request):
    blinks = Brand.objects.all()
    return dict(blinks=blinks)
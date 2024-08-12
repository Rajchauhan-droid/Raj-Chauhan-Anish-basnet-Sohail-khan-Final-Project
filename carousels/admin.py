from django.contrib import admin

# Register your models here.
from .models import Carousel


class CarouselAdmin(admin.ModelAdmin):
    list_display = ('title', 'image')


admin.site.register(Carousel, CarouselAdmin)
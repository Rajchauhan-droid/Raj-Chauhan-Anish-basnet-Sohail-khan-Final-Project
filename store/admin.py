from django.contrib import admin
from .models import Product,Variation,ReviewRating, ProductGallery
import admin_thumbnails
from django.db import models
from django_summernote.widgets import SummernoteWidget 
# Register your models here.

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = list_display = ('product_name', 'marked_price', 'stock', 'category', 'modified_date', 'is_available')
    filter_horizontal = ('related_products',)
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]
    formfield_overrides = { 
            models.TextField: {'widget': SummernoteWidget}, 
     } 
    

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')


admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
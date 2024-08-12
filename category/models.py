from django.db import models
from django.urls import reverse
# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to = 'photos/categories',blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
            return reverse('store_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name
    

    
    
class Sub_Category(models.Model):
     category = models.ForeignKey(Category, on_delete=models.CASCADE)
     sub_name = models.CharField(max_length=255, blank=True)
     subslug = models.SlugField(max_length=100, unique=True)


     class Meta:
        verbose_name = 'sub_category'
        verbose_name_plural = 'sub_categories'

     def get_url(self):
            return reverse('products_by_sub_category', args=[self.subslug])
     
     def __str__(self):
          return self.sub_name
     
     def __str__(self):
          return self.category.category_name + " -- " + self.sub_name
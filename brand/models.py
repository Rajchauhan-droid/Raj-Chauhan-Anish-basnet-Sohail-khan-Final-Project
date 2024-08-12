from django.db import models
from django.urls import reverse
# Create your models here.
from django.utils.text import slugify


class Brand(models.Model):
    brand_name = models.CharField(max_length=50, unique=True)
    brandslug = models.SlugField(max_length=100, unique=True)
    brand_image = models.ImageField(upload_to = 'photos/brand_image',blank=True)

    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'

    def get_url(self):
            return reverse('store_by_brand', args=[self.brandslug])

    def __str__(self):
        return self.brand_name


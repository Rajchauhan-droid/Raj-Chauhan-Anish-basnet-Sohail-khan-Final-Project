from django.db import models

# Create your models here.
class Carousel(models.Model):
    image = models.ImageField(upload_to="banner_imgs/")
    title = models.CharField(max_length=150)
    action_name = models.CharField(max_length=50)
    sub_title = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Carousel'

    def __str__(self):
        return self.title
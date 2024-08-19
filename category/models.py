from django.db import models
from django.urls import reverse
# Create your models here.

class category(models.Model):
    category_name = models.CharField(max_length=100,unique= True)
    slug = models.SlugField(max_length = 100, unique= True)
    category_description = models.TextField(max_length=300, blank = True)
    category_img = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_urls(self):
            return reverse('products_by_category', args =[self.slug])

    def __str__(self):
        return self.category_name
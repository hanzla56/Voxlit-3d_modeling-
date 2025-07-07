from django.db import models
from tinymce.models import HTMLField 
from tinymce import models as tinymce_models
from django.utils.text import slugify

# Create your models here.
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    sub_heading = models.CharField(max_length=200,blank=True, null=True)
    short_description = models.CharField(max_length=200,blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=200, blank=True, null=True)
    content = tinymce_models.HTMLField()
    published_date = models.DateTimeField(auto_now_add=True)
    is_trending = models.BooleanField(default=False)
    main_image = models.ImageField(upload_to='blog_images/')


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
          return self.title
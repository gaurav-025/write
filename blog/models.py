from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.crypto import get_random_string
import math
from django.utils.html import strip_tags

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    bio=models.TextField(blank=True)
    profile_image=models.ImageField(upload_to='profile_images/',blank=True,null=True)

    def __str__(self):
        return self.user.username

class Tag(models.Model):
    name=models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    slug=models.SlugField(unique=True,blank=True)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    tags=models.ManyToManyField(Tag,blank=True)
    content_html=models.TextField(blank=True)

    @property
    def read_time(self):
        word_count=len(strip_tags(self.content).split())
        minutes=math.ceil(word_count/200)
        return f"{minutes} min read"

    def save(self,*args,**kwargs):
        if not self.slug:
            base_slug=slugify(self.title)
            slug=base_slug
            num=1
            while Post.objects.filter(slug=slug).exists():
                slug=f"{base_slug}-{get_random_string(8)}"
            self.slug=slug
        super(Post,self).save(*args,**kwargs)
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    post=models.ForeignKey('Post',on_delete=models.CASCADE,related_name='comments')
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    name=models.CharField(max_length=80,blank=True)
    body=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user or self.name} on {self.post}"


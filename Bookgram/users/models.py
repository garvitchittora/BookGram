from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.utils import timezone

class User(AbstractUser):
    slug=models.SlugField(max_length=250,null=True,blank=True,unique=True)
    email = models.EmailField(_('email address'), unique=True)
    image = models.ImageField(upload_to ='static/userImage/', null=True, blank=True)

def createSlug(instance,new_slug=None):
    string=instance.first_name+"-"+instance.last_name
    slug=slugify(string)
    if new_slug is not None:
        slug=new_slug

    qs=User.objects.filter(slug=slug).order_by("-id")
    exists=qs.exists()
    if exists:
        new_slug="%s-%s" %(slug , qs.first().id)
        return createSlug(instance,new_slug=new_slug)             
    return slug

def slug_generator(sender,instance,*arg,**k):
    instance.username=instance.email
    if not instance.slug:
        instance.slug=createSlug(instance)

pre_save.connect(slug_generator,sender=User)  

class post(models.Model):
    user= models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    caption = models.CharField( max_length=10000, null=True, blank=True)
    bookid = models.CharField( max_length=100, null=True, blank=True)
    created_date = models.DateTimeField('date created', default=timezone.now)
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.

SHOES = 'shoes'
CLOTHES = 'clothes'
ACCESSORIES = 'accessories'

CATEGORY = (
    (SHOES,'shoes'),
    (CLOTHES,'clothes'),
    (ACCESSORIES,'accessories')
)

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_category = models.CharField(choices=CATEGORY,max_length=100,default=SHOES)
    product_price = models.FloatField()
    thumbnail = models.ImageField(blank=False)
    date_added = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.product_name

class Cart(models.Model):
    user = models.OneToOneField(User, models.CASCADE, blank=True)
    created_at = models.DateTimeField(default=datetime.now())
    product = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return self.user.username

class Favourite(models.Model):
    user = models.OneToOneField(User, models.CASCADE, blank=True)
    product = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return self.user.username

class New_Arrival(models.Model):
    product_name = models.CharField(max_length=100)
    product_price = models.FloatField()
    thumbnail = models.ImageField(blank=False)
    date_added = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.product_name

#mpesa payments records
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
# M-pesa Payment models
class MpesaCalls(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()
    class Meta:
        verbose_name = 'Mpesa Call'
        verbose_name_plural = 'Mpesa Calls'
class MpesaCallBacks(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()
    class Meta:
        verbose_name = 'Mpesa Call Back'
        verbose_name_plural = 'Mpesa Call Backs'
class MpesaPayment(BaseModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    type = models.TextField()
    reference = models.TextField()
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.TextField()
    organization_balance = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'
    def __str__(self):
        return self.first_name        
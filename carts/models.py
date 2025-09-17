from django.db import models
from store.models import Product, Variation
from accounts.models import Account
from django.conf import settings



# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id
    

class CartItem(models.Model):
    # Use AUTH_USER_MODEL so it always points to your custom Account model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, null=True, blank=True)  # made nullable
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    

    
    def sub_total(self):
        return self.product.price * self.quantity
    
    
    def __unicode__(self):
        return self.product
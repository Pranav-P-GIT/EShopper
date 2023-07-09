from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE, null=True, blank=True)
    name= models.CharField(max_length=200,null=True)
    email= models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.name

    
class Product(models.Model):
    name= models.CharField(max_length=200,null=True)
    image=models.ImageField(null=True,blank=True)
    price= models.FloatField()
    digital= models.BooleanField(default=False,null=True,blank=False)
    
    
    def __str__(self):
        return self.name
    

class Order(models.Model):
    customer= models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True)
    date_ordered= models.DateTimeField(auto_now_add=True)
    complete=models.BooleanField(default=False,null=True,blank=False)
    transaction_id= models.CharField(max_length=200,null=True)
    
    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems=self.orderitem_set.all()
        total=sum([i.get_total for i in orderitems])
        return total
    @property
    def get_cart_items(self):
        orderitems=self.orderitem_set.all()
        total=sum([i.quantity for i in orderitems])
        return total

class OrderItem(models.Model):
    product= models.ForeignKey(Product, on_delete=models.SET_NULL,null=True)  
    order= models.ForeignKey(Order, on_delete=models.SET_NULL,null=True)
    quantity= models.IntegerField(default=0,null=True,blank=True)   
    date_added=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.product.name} ({self.quantity})'
    
    @property
    def get_total(self):
        total= self.product.price * self.quantity
        return total
    
    
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,null=True)
    address= models.CharField(max_length=200,null=True)
    city= models.CharField(max_length=200,null=True)
    state= models.CharField(max_length=200,null=True)
    zipcode= models.CharField(max_length=200,null=True)
    date_added=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.address
    
    

    
class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f'Comment by {self.name} on {self.product}'

    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.name  



from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(null=True)
    contact_number = models.CharField(max_length=15,null=True)
    is_approved = models.BooleanField(default=False,null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Category(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    url = models.CharField(max_length=100)
    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE)
    downloadable = models.BooleanField(default=False)
    zip_file = models.FileField(upload_to='products/zips/', null=True, blank=True)

    # New fields
    image = models.ImageField(upload_to='products/images/', null=True, blank=True)  # Product image
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)  # Product rating (out of 5)
    review_count = models.PositiveIntegerField(default=0)  # Total number of reviews
    product_specification = models.TextField(null=True, blank=True)  # New specification field

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Cart of {self.user.username}"


class Order(models.Model):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    qr_code_image = models.ImageField(upload_to='orders/qr_codes/', null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} for {self.user.username}"
from django.db import models
from django.utils import timezone

# Create your models here.

class Login(models.Model):
    uname=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    user_type=models.CharField(max_length=200)
    def __str__(self):
        return self.uname

class Package(models.Model):
    title=models.CharField(max_length=200)
    photo=models.ImageField(upload_to='package')
    description=models.CharField(max_length=2000)
    price=models.CharField(max_length=200,null=True)
    duration=models.CharField(max_length=200,null=True)
    noofperson=models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.title

class Boat(models.Model):
    price=models.CharField(max_length=200)
    photo=models.ImageField(upload_to='boats')
    description=models.CharField(max_length=2000)
    category=models.CharField(max_length=200, default='pending')
    def __str__(self):
        return self.price

class Room(models.Model):
    price=models.CharField(max_length=200)
    photo=models.ImageField(upload_to='rooms')
    description=models.CharField(max_length=2000)
    category=models.CharField(max_length=200, default='pending')
    def __str__(self):
        return self.price
    
class Gallery(models.Model):
    photo=models.ImageField(upload_to='gallery')
    
class Testimonial(models.Model):
    name=models.CharField(max_length=200)
    decription=models.CharField(max_length=2000)
    photo=models.ImageField(upload_to='testimonial')
    
class Destination(models.Model):
    name=models.CharField(max_length=200)
    photo=models.ImageField(upload_to='destination')

class Bookingcount(models.Model):
    booking_count=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.booking_count


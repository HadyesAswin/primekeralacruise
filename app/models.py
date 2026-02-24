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
    status=models.CharField(max_length=200,null=True)
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
    

class Tariff(models.Model):
    CATEGORY_CHOICES = [
        ('Deluxe', 'Deluxe'),
        ('Premium', 'Premium'),
        ('Luxury', 'Luxury'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    room_count = models.CharField(max_length=200)
    amount = models.CharField(max_length=200)
    type = models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.room_count
    


class Tariff1(models.Model):
    CATEGORY_CHOICES = [
        ('Deluxe', 'Deluxe'),
        ('Premium', 'Premium'),
        ('Luxury', 'Luxury'),
    ]
    TYPE_CHOICES = [
        ('DayCruise', 'DayCruise'),
        ('OvernightCruise', 'OvernightCruise'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)

    # Shared fields
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # For Day Cruise
    base_people = models.PositiveIntegerField(null=True, blank=True)
    extra_person_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # For Overnight Cruise
    room_count = models.PositiveIntegerField(null=True, blank=True)
    extra_person_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.category} - {self.type}"

    def get_display_name(self):
        if self.type == "DayCruise":
            return f"{self.category}: ₹{self.amount} for {self.base_people} person(s), +₹{self.extra_person_amount}/extra"
        else:
            return f"{self.category} - {self.room_count} Bedroom: ₹{self.amount}"

    


class MenuItem(models.Model):
    CRUISE_CHOICES = [
        ('day', 'Day Cruise'),
        ('overnight', 'Overnight Cruise'),
    ]

    PACKAGE_CHOICES = [
        ('deluxe', 'Deluxe'),
        ('premium', 'Premium'),
        ('luxury', 'Luxury'),
    ]

    cruise_type = models.CharField(max_length=20, choices=CRUISE_CHOICES)
    package_type = models.CharField(max_length=20, choices=PACKAGE_CHOICES)
    item_name = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    time_slot = models.CharField(max_length=50, blank=True)
    is_special = models.CharField(max_length=100,null=True)
    duration = models.CharField(max_length=50, blank=True)
    ac_available = models.CharField(max_length=100,null=True)
    image=models.ImageField(upload_to='menu')
    order_number = models.PositiveIntegerField(default=0,null=True)

    def __str__(self):
        return f"{self.cruise_type.title()} - {self.package_type.title()} - {self.item_name}"



class PackageBooking(models.Model):
    fullname = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    from_date = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    booking_item = models.CharField(max_length=200, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fullname} - {self.booking_item or 'Package'}"
    

class BoatBooking(models.Model):
    fullname = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    from_date = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    bedroom = models.CharField(max_length=50)
    noofadult = models.PositiveIntegerField()
    noofchild = models.PositiveIntegerField()
    category = models.CharField(max_length=100)
    cruise_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fullname} - {self.bedroom}"    
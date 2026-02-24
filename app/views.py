import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from twilio.rest import Client
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login

from datetime import datetime
# Create your views here.


# -----------------------------------Public functions----------------------------------


def custom_404(request, exception):
    return render(request, 'public/404.html', status=404)

def logout(request):
    request.session['log']="out"
    return HttpResponse("<script>alert('Logout'); window.location='/login'</script>")


def index(request):
    request.session['log']="out"
    boats = Boat.objects.filter(status='active')
    packages = Package.objects.all()[:3]
    photos = Gallery.objects.all()
    destinations = Destination.objects.all()[:6]
    testimonials = Testimonial.objects.all()
    gallery = Gallery.objects.all()[:6]
    styles = ['item-1', 'item-2', 'item-3', 'item-4', 'item-5', 'item-6']
    for i, item in enumerate(gallery):
        item.item_class = styles[i % len(styles)]
 # show only 6 packages
    return render(request, 'public/home2.html', {
        'boats': boats,
        'packages': packages,
        'photos': photos,
        'destinations': destinations,
        'testimonials': testimonials,
        'gallery': gallery
    })


def login(request):
    request.session['log']="out"
    if 'submit' in request.POST:
        uname=request.POST['username']
        password=request.POST['password']
        if Login.objects.filter(uname=uname,password=password).exists():
            s=Login.objects.get(uname=uname,password=password)
            request.session["lid"]=s.pk
            lid=request.session.get('lid')
            if s.user_type == "admin":
                request.session['log']="in"
                return HttpResponse(f"<script>alert('Welcome Admin');window.location='/admin_home'</script>")
            else:
                return HttpResponse(f"<script>alert('Invalid user...!');window.location='/login'</script>")
        else:
            return HttpResponse(f"<script>alert('Username or password incorrect...!');window.location='/login'</script>")
    return render(request,'public/login.html')



# def login(request):
#     if request.method == 'POST':
#         uname = request.POST['username']
#         password = request.POST['password']

#         user = authenticate(request, username=uname, password=password)

#         if user is not None:
#             auth_login(request, user)
#             if user.is_superuser:
#                 messages.success(request, 'Welcome Admin!')
#                 return redirect('/admin_home')
#             else:
#                 messages.error(request, 'You are not authorized as admin.')
#                 return redirect('/login')
#         else:
#             messages.error(request, 'Invalid username or password.')
#             return redirect('/login')

#     return render(request, 'public/login.html')

# -----------------------------------User functions----------------------------------


# def tariffs(request):
#     return render(request,'public/tariff.html')

# def tariffs(request):
#     deluxe_prices = Tariff.objects.filter(category="Deluxe")
#     premium_prices = Tariff.objects.filter(category="Premium")
#     luxury_prices = Tariff.objects.filter(category="Luxury")

#     return render(request, 'public/tariff.html', {
#         'deluxe_prices': deluxe_prices,
#         'premium_prices': premium_prices,
#         'luxury_prices': luxury_prices,
#     })

def tariffs(request):
    # Day Cruise
    deluxe_day = Tariff1.objects.filter(category="Deluxe", type="DayCruise")
    premium_day = Tariff1.objects.filter(category="Premium", type="DayCruise")
    luxury_day = Tariff1.objects.filter(category="Luxury", type="DayCruise")

    # Overnight Cruise
    deluxe_night = Tariff1.objects.filter(category="Deluxe", type="OvernightCruise")
    premium_night = Tariff1.objects.filter(category="Premium", type="OvernightCruise")
    luxury_night = Tariff1.objects.filter(category="Luxury", type="OvernightCruise")

    return render(request, 'public/tariff.html', {
        'deluxe_day': deluxe_day,
        'premium_day': premium_day,
        'luxury_day': luxury_day,
        'deluxe_night': deluxe_night,
        'premium_night': premium_night,
        'luxury_night': luxury_night
    })

# def booknow(request):
#     boats = Boat.objects.all()  # Fetch all boats
#     categories = ['Deluxe', 'Premium', 'Luxury']
#     cruise_types = ['Day Cruise', 'Overnight Cruise']
    
#     return render(request, 'public/booknow.html', {
#         'boats': boats,
#         'categories': categories,
#         'cruise_types': cruise_types
#     })


# def commonbooking(request):
#     boats = Boat.objects.all()  # Fetch all boats
#     categories = ['Deluxe', 'Premium', 'Luxury']
#     cruise_types = ['Day Cruise', 'Overnight Cruise']
    
#     return render(request, 'public/commonbooking.html', {
#         'boats': boats,
#         'categories': categories,
#         'cruise_types': cruise_types
#     })


import razorpay
from django.views.decorators.csrf import csrf_exempt

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def booknow(request):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        place = request.POST.get('place')
        from_date = request.POST.get('from_date')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        booking_item = request.POST.get('booking_item')

        # 1. EXTRACT PACKAGE AND CALCULATE 10%
        advance_amount = 1000  # A safe fallback amount in case something goes wrong

        if booking_item:
            # If your HTML passes "Category, Item", this safely grabs just the "Item"
            item_name = booking_item.split(',')[-1].strip()
            package = Package.objects.filter(title__icontains=item_name).first()

            if package and package.price:
                try:
                    # Clean the string: remove commas, currency symbols, and spaces
                    clean_price = package.price.replace(',', '').replace('₹', '').replace('Rs', '').strip()
                    total_price = float(clean_price)
                    
                    # Calculate 10%
                    advance_amount = round(total_price * 0.10, 2)
                except ValueError:
                    pass # Keep the fallback amount if the price string is completely invalid

        # 2. CREATE RAZORPAY ORDER
        # Note: Razorpay requires the amount in paise (multiply by 100) and it must be an integer
        order = client.order.create({
            "amount": int(advance_amount * 100),  
            "currency": "INR",
            "payment_capture": "1"
        })

        # 3. SAVE BOOKING
        booking = PackageBooking.objects.create(
            fullname=fullname,
            place=place,
            from_date=from_date,
            phone=phone,
            email=email,
            booking_item=booking_item,
            amount=advance_amount,
            order_id=order["id"]
        )

        context = {
            "booking": booking,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": int(advance_amount * 100),
            "display_amount": advance_amount,
            "order_id": order["id"],
            "name": fullname,
            "email": email,
            "phone": phone
        }

        return render(request, "public/payment_page.html", context)

    return render(request, 'public/booknow.html')


# def commonbooking(request):
#     boats = Boat.objects.all()
#     categories = ['Deluxe', 'Premium', 'Luxury']
#     cruise_types = ['Day Cruise', 'Overnight Cruise']

#     if request.method == "POST":
#         fullname = request.POST.get('fullname')
#         place = request.POST.get('place')
#         from_date = request.POST.get('from_date')
#         phone = request.POST.get('phone')
#         email = request.POST.get('email')
#         bedroom = request.POST.get('bedroom')
#         noofadult = request.POST.get('noofadult')
#         noofchild = request.POST.get('noofchild')
#         category = request.POST.get('category')
#         cruise_type = request.POST.get('cruise_type')

#         # 1. GET BOAT PRICE AND CALCULATE 10%
#         selected_boat = Boat.objects.filter(description=bedroom).first()
#         advance_amount = 1000  # Safe fallback

#         if selected_boat and selected_boat.price:
#             try:
#                 # Clean the string: remove commas, currency symbols, and spaces
#                 clean_price = selected_boat.price.replace(',', '').replace('₹', '').replace('Rs', '').strip()
#                 total_price = float(clean_price)
                
#                 # Calculate 10%
#                 advance_amount = round(total_price * 0.10, 2)
#             except ValueError:
#                 pass # Keep the fallback amount if the price string is invalid

#         # 2. CREATE RAZORPAY ORDER
#         order = client.order.create({
#             "amount": int(advance_amount * 100),
#             "currency": "INR",
#             "payment_capture": "1"
#         })

#         # 3. SAVE BOOKING
#         booking = BoatBooking.objects.create(
#             fullname=fullname,
#             place=place,
#             from_date=from_date,
#             phone=phone,
#             email=email,
#             bedroom=bedroom,
#             noofadult=noofadult,
#             noofchild=noofchild,
#             category=category,
#             cruise_type=cruise_type,
#             amount=advance_amount,
#             order_id=order["id"],
#             payment_status="pending"
#         )

#         context = {
#             "booking": booking,
#             "razorpay_key": settings.RAZORPAY_KEY_ID,
#             "amount": int(advance_amount * 100),
#             "display_amount": advance_amount,
#             "order_id": order["id"],
#             "name": fullname,
#             "email": email,
#             "phone": phone
#         }

#         return render(request, "public/payment_page.html", context)

#     return render(request, 'public/commonbooking.html', {
#         'boats': boats,
#         'categories': categories,
#         'cruise_types': cruise_types,
#     })

def commonbooking(request):
    boats = Boat.objects.all()
    categories = ['Deluxe', 'Premium', 'Luxury']
    cruise_types = ['Day Cruise', 'Overnight Cruise']

    if request.method == "POST":
        fullname = request.POST.get('fullname')
        place = request.POST.get('place')
        from_date = request.POST.get('from_date')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        bedroom = request.POST.get('bedroom')
        noofadult = request.POST.get('noofadult')
        noofchild = request.POST.get('noofchild')
        category = request.POST.get('category')
        cruise_type = request.POST.get('cruise_type')

        # 1. SET FIXED ADVANCE AMOUNT
        advance_amount = 1500

        # 2. CREATE RAZORPAY ORDER
        order = client.order.create({
            "amount": int(advance_amount * 100), # Razorpay expects paise, so 150000
            "currency": "INR",
            "payment_capture": "1"
        })

        # 3. SAVE BOOKING
        booking = BoatBooking.objects.create(
            fullname=fullname,
            place=place,
            from_date=from_date,
            phone=phone,
            email=email,
            bedroom=bedroom,
            noofadult=noofadult,
            noofchild=noofchild,
            category=category,
            cruise_type=cruise_type,
            amount=advance_amount,
            order_id=order["id"],
            payment_status="pending"
        )

        context = {
            "booking": booking,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": int(advance_amount * 100),
            "display_amount": advance_amount,
            "order_id": order["id"],
            "name": fullname,
            "email": email,
            "phone": phone
        }

        return render(request, "public/payment_page.html", context)

    return render(request, 'public/commonbooking.html', {
        'boats': boats,
        'categories': categories,
        'cruise_types': cruise_types,
    })

def ajax_available_boats(request):
    selected_date_str = request.GET.get('from_date')
    if not selected_date_str:
        return JsonResponse({'error': 'No date provided'}, status=400)

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    # Get all boats
    boats = Boat.objects.all()

    # Get all bedrooms already booked on this date
    booked_boats = BoatBooking.objects.filter(from_date=selected_date).values_list('bedroom', flat=True)

    data = []
    for boat in boats:
        data.append({
            'description': boat.description,
            'available': boat.description not in booked_boats
        })

    return JsonResponse({'boats': data})


import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.mail import send_mail

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def payment_success(request):
    if request.method == "POST":

        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # VERIFY SIGNATURE
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except:
            return render(request, "public/payment_failed.html")

        # If signature valid, continue
        booking = PackageBooking.objects.filter(order_id=razorpay_order_id).first()
        if not booking:
            booking = BoatBooking.objects.filter(order_id=razorpay_order_id).first()

        if booking:
            booking.payment_id = razorpay_payment_id
            booking.payment_status = "paid"
            booking.save()

            # Send emails
            send_booking_emails(booking)

        return render(request, "public/payment_success.html", {"booking": booking})

def send_booking_emails(booking):

    user_subject = "Booking Payment Successful"
    user_message = f"""
Hi {booking.fullname},

Your booking payment of ₹{booking.amount} was successful.

Payment ID: {booking.payment_id}
Order ID: {booking.order_id}
Date: {booking.from_date}

Thank you for booking with Prime Kerala Cruise!
"""
    send_mail(user_subject, user_message, settings.DEFAULT_FROM_EMAIL, [booking.email])

    admin_subject = f"New Booking Received - Order ID {booking.order_id}"
    admin_message = f"""
Full Name: {booking.fullname}
Phone: {booking.phone}
Email: {booking.email}
Amount: ₹{booking.amount}
Payment ID: {booking.payment_id}
"""
    send_mail(admin_subject, admin_message, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])







def boatsharing(request):
    categories = ['Deluxe', 'Premium', 'Luxury']
    cruise_types = ['Day Cruise', 'Overnight Cruise']

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        place = request.POST.get('place')
        from_date = request.POST.get('from_date')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        noofadult = request.POST.get('noofadult')
        noofchild = request.POST.get('noofchild')
        category = request.POST.get('category')
        cruise_type = request.POST.get('cruise_type')

        # 📨 Email content
        subject = f"Boat Sharing Enquiry from {fullname}"
        message = f"""
New Boat Sharing Enquiry Received:

👤 Full Name: {fullname}
📍 Place: {place}
📅 Date: {from_date}
📞 Phone: {phone}
📧 Email: {email}
👪 Number of Adults: {noofadult}
🧒 Number of Children: {noofchild}
🚢 Category: {category}
⚓ Cruise Type: {cruise_type}
"""
        sender = 'primekeralacruise@gmail.com'
        recipient = ['primekeralacruise@gmail.com']

        try:
            send_mail(subject, message, sender, recipient, fail_silently=False)
            messages.success(request, "✅ Thank you! We’ll contact you soon for confirmation.")
        except Exception as e:
            messages.error(request, f"❌ Failed to send email. Error: {e}")

        return redirect('boatsharing')  # redirect to same page after submission

    return render(request, 'public/boatsharing.html', {
        'categories': categories,
        'cruise_types': cruise_types
    })


# def allpackages(request):
#     packages = Package.objects.all()
#     paginator = Paginator(packages, 6)  # Show 6 packages per page
#     page_number = request.GET.get('page')  # ?page=2
#     page_obj = paginator.get_page(page_number)
    
#     return render(request, 'public/allpackages.html', {'page_obj': page_obj})


def allpackages(request):
    # Existing Packages Pagination
    packages = Package.objects.all()
    paginator = Paginator(packages, 6)  # Show 6 packages per page
    page_number = request.GET.get('page')  # ?page=2
    page_obj = paginator.get_page(page_number)

    # Boats Pagination
    boats = Boat.objects.filter(status='active')
    boat_paginator = Paginator(boats, 6)
    boat_page_number = request.GET.get('boat_page')
    boats_page_obj = boat_paginator.get_page(boat_page_number)

    return render(request, 'public/allpackages.html', {
        'page_obj': page_obj,
        'boats_page_obj': boats_page_obj,
    })

def allboats(request):
    boats = Boat.objects.all()
    paginator = Paginator(boats, 6)  # Show 6 packages per page
    page_number = request.GET.get('page')  # ?page=2
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'public/allboats.html', {'page_obj': page_obj})

def alldestinations(request):
    destinations = Destination.objects.all()
    return render(request,'public/alldestinations.html', {'destinations': destinations})

def aboutus(request):
    return render(request,'public/aboutus.html')

def allgallery(request):
    gallery = Gallery.objects.all()
    return render(request,'public/allgallery.html', {'gallery': gallery})

# def menu(request):
#     return render(request,'public/menu.html')

# def menu(request):
#     cruise = request.GET.get('cruise')     # e.g. 'day' or 'overnight'
#     package = request.GET.get('package')   # e.g. 'deluxe', 'premium', 'luxury'

#     # Start with all items
#     menu_items = MenuItem.objects.all()

#     # Filter if parameters exist
#     if cruise:
#         menu_items = menu_items.filter(cruise_type__iexact=cruise)
#     if package:
#         menu_items = menu_items.filter(package_type__iexact=package)

#     return render(request, 'public/menu.html', {'menu_items': menu_items})


# def menu(request):
#     cruise_type = request.GET.get('cruise')
#     package_type = request.GET.get('package')

#     # Base queryset — ordered by order_number
#     menu_items = MenuItem.objects.all().order_by('cruise_type', 'package_type', 'order_number')

#     # Apply filters
#     if cruise_type:
#         menu_items = menu_items.filter(cruise_type__iexact=cruise_type)
#     if package_type:
#         menu_items = menu_items.filter(package_type__iexact=package_type)

#     # Group by cruise_type + package_type
#     grouped_dict = {}

#     for item in menu_items:
#         key = (item.cruise_type, item.package_type)
#         if key not in grouped_dict:
#             grouped_dict[key] = {
#                 'cruise_type': item.get_cruise_type_display(),
#                 'package_type': item.get_package_type_display(),
#                 'image': item.image,
#                 'items': []
#             }
#         grouped_dict[key]['items'].append(item)

#     # 🔽 Sort each group's items by order_number explicitly
#     for group in grouped_dict.values():
#         group['items'].sort(key=lambda x: x.order_number or 0)

#     # 🔽 Sort the groups themselves by the *lowest order number* in each group
#     grouped_menus = sorted(grouped_dict.values(), key=lambda g: g['items'][0].order_number if g['items'] else 9999)

#     context = {"grouped_menus": grouped_menus}
#     return render(request, "public/menu.html", context)


from collections import defaultdict

def menu(request):
    cruise = request.GET.get('cruise')
    package = request.GET.get('package')

    queryset = MenuItem.objects.all()

    if cruise:
        queryset = queryset.filter(cruise_type=cruise)
    if package:
        queryset = queryset.filter(package_type=package)

    grouped = defaultdict(list)
    for item in queryset:
        key = (item.cruise_type, item.package_type)
        grouped[key].append(item)

    grouped_menus = []
    for (cruise_type, package_type), items in grouped.items():
        # Collect first special and AC details once
        first_special = next((i.is_special for i in items if i.is_special), None)
        first_ac = next((i.ac_available for i in items if i.ac_available), None)
        first_duration = next((i.duration for i in items if i.duration), None)
        first_time_slot = next((i.time_slot for i in items if i.time_slot), None)
        first_image = next((i.image for i in items if i.image), None)

        grouped_menus.append({
            'cruise_type': cruise_type.title(),
            'package_type': package_type.title(),
            'items': items,
            'first_special': first_special,
            'first_ac': first_ac,
            'first_duration': first_duration,
            'first_time_slot': first_time_slot,
            'image': first_image,
        })

    return render(request, 'public/menu.html', {
        'grouped_menus': grouped_menus
    })




def faq(request):
    return render(request,'public/faq.html')

def termsandcondition(request):
    return render(request,'public/termscondition.html')

# def contactus(request):
#     return render(request,'public/contactus.html')

def contactus(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f'New Contact Form Submission from {name}'
        body = f'''
You have received a new message from your website contact form:

Name: {name}
Email: {email}

Message:
{message}
'''

        try:
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,  # from
                ['primekeralacruise@gmail.com'],  # to
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')

        return redirect('contactus')

    return render(request, 'public/contactus.html')


# -----------------------------------Admin functions----------------------------------

from datetime import timedelta
from django.utils import timezone

# def admin_view_booking_count(request):
#     now = timezone.now()
#     one_week_ago = now - timedelta(weeks=1)
#     one_month_ago = now - timedelta(days=30)

#     weekly_count = Bookingcount.objects.filter(booking_count__gte=one_week_ago).count()
#     monthly_count = Bookingcount.objects.filter(booking_count__gte=one_month_ago).count()
#     return render(request, 'admin/admin_view_booking_count.html', {'weekly_count':weekly_count,'monthly_count':monthly_count})

# def admin_home(request):
#     return render(request,'admin/admin_home.html')

def admin_home(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    now = timezone.now()
    one_week_ago = now - timedelta(days=7)
    one_month_ago = now - timedelta(days=30)

    # Count rows where booking_count datetime is within the range
    weekly_count = Bookingcount.objects.filter(booking_count__gte=one_week_ago).count()
    monthly_count = Bookingcount.objects.filter(booking_count__gte=one_month_ago).count()

    counts = {'weekly': weekly_count, 'monthly': monthly_count}
    return render(request, 'admin/admin_home.html', {'counts': counts})


def admin_view_package(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    packages = Package.objects.all()
    return render(request, 'admin/admin_view_package.html', {'packages': packages})




def admin_add_package(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    if request.method == 'POST':
        title = request.POST.get('title')
        photo = request.FILES.get('photo')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration = request.POST.get('duration')
        noofperson = request.POST.get('person')
        Package.objects.create(
            title=title,
            photo=photo,
            description=description,
            price=price,
            duration=duration,
            noofperson=noofperson
        )
        return redirect('admin_view_package')
    return render(request, 'admin/admin_add_package.html')


def admin_edit_package(request, id):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    package = Package.objects.get(id=id)
    if request.method == 'POST':
        package.title = request.POST.get('title')
        package.description = request.POST.get('description')
        package.price = request.POST.get('price')
        package.duration = request.POST.get('duration')
        package.noofperson = request.POST.get('person')
        if 'photo' in request.FILES:
            # print("got photo")
            package.photo = request.FILES['photo']
        package.save()
        return redirect('admin_view_package')
    return render(request, 'admin/admin_edit_package.html', {'package': package})


def admin_delete_package(request, id):
    package = Package.objects.get(id=id)
    package.delete()
    return redirect('admin_view_package')


def admin_add_boat(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    if request.method == 'POST':
        price = request.POST.get('price')
        photo = request.FILES.get('photo')
        description = request.POST.get('description')
        category = request.POST.get('category')
        Boat.objects.create(
            price=price,
            photo=photo,
            description=description,
            category=category,
            status="active"
        )
        return redirect('admin_view_boat')
    return render(request, 'admin/admin_add_boat.html')


def admin_view_boat(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    boats = Boat.objects.all()
    return render(request, 'admin/admin_view_boat.html', {'boats': boats})


def admin_edit_boat(request, id):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    boat = Boat.objects.get(id=id)
    if request.method == 'POST':
        boat.price = request.POST.get('price')
        boat.description = request.POST.get('description')
        boat.category = request.POST.get('category')
        if 'photo' in request.FILES:
            boat.photo = request.FILES['photo']
        boat.save()
        return redirect('admin_view_boat')
    return render(request, 'admin/admin_edit_boat.html', {'boat': boat})


def admin_delete_boat(request, id):
    boat = Boat.objects.get(id=id)
    boat.delete()
    return redirect('admin_view_boat')


def admin_toggle_boat_status(request, boat_id):
    boat = get_object_or_404(Boat, id=boat_id)
    if boat.status == 'active':
        boat.status = 'blocked'
    else:
        boat.status = 'active'
    boat.save()
    return redirect('admin_view_boat') 

def admin_view_room(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    rooms = Room.objects.all()
    return render(request, 'admin/admin_view_room.html', {'rooms': rooms})


def admin_add_room(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    if request.method == 'POST':
        price = request.POST.get('price')
        photo = request.FILES.get('photo')
        description = request.POST.get('description')
        category = request.POST.get('category')
        Room.objects.create(
            price=price,
            photo=photo,
            description=description,
            category=category
        )
        return redirect('admin_view_room')
    return render(request, 'admin/admin_add_room.html')


def admin_edit_room(request, id):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    room = Room.objects.get(id=id)
    if request.method == 'POST':
        room.price = request.POST.get('price')
        room.description = request.POST.get('description')
        room.category = request.POST.get('category')
        if 'photo' in request.FILES:
            room.photo = request.FILES['photo']
        room.save()
        return redirect('admin_view_room')
    return render(request, 'admin/admin_edit_room.html', {'room': room})


def admin_delete_room(request, id):
    room = Room.objects.get(id=id)
    room.delete()
    return redirect('admin_view_room')


def admin_view_gallery(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    photos = Gallery.objects.all()
    return render(request, 'admin/admin_view_gallery.html', {'photos': photos})


def admin_add_gallery(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    if request.method == "POST":
        photo = request.FILES.get('photo')
        if photo:
            Gallery.objects.create(photo=photo)
            return redirect('admin_view_gallery')
    return render(request, 'admin/admin_add_gallery.html')


def admin_edit_gallery(request, id):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    photo = Gallery.objects.get(id=id)
    if request.method == 'POST':
        if 'photo' in request.FILES:
            photo.photo = request.FILES['photo']
        photo.save()
        return redirect('admin_view_gallery')
    return render(request, 'admin/admin_edit_gallery.html', {'gallery_item': photo})

def admin_delete_gallery(request, id):
    photo = Gallery.objects.get(id=id)
    photo.delete()
    return redirect('admin_view_gallery')


def admin_view_testimonial(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    testimonials = Testimonial.objects.all()
    return render(request, 'admin/admin_view_testimonial.html', {'testimonials': testimonials})


def admin_add_testimonial(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        photo = request.FILES.get('photo')
        if name and description and photo:
            Testimonial.objects.create(
                name=name,
                decription=description,
                photo=photo
            )
            return redirect('admin_view_testimonial')
    return render(request, 'admin/admin_add_testimonial.html')



def admin_edit_testimonial(request, id):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    testimonial = Testimonial.objects.get(id=id)
    if request.method == "POST":
        name = request.POST.get('name')
        decription = request.POST.get('decription')
        photo = request.FILES.get('photo')
        if name:
            testimonial.name = name
        if decription:
            testimonial.decription = decription
        if photo:
            testimonial.photo = photo
        testimonial.save()
        return redirect('admin_view_testimonial')
    return render(request, 'admin/admin_edit_testimonial.html', {'testimonial': testimonial})

def admin_delete_testimonial(request, id):
    testimonial = Testimonial.objects.get(id=id)
    testimonial.delete()
    return redirect('admin_view_testimonial')


@csrf_exempt
def chatbot_api(request):
    """Handles the chatbot conversation logic."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('message', '').lower()
            conversation_state = data.get('state', 'start')

            response_data = {}
            booking_details = data.get('booking_details', {})

            # === Conversation flow ===
            if conversation_state == 'start':
                response_data = {
                    'response': "👋",
                    'new_state': 'welcome',
                    'booking_details': booking_details
                }

            elif conversation_state == 'welcome':
                response_data = {
                    'response': "Hello! I can help you with your backwater trip. What type of boat would you like to book?",
                    'options': [
                        {'text': 'Houseboat 🏠', 'value': 'houseboat'},
                        {'text': 'Motorboat 🚤', 'value': 'motorboat'},
                        {'text': 'Speedboat 🚀', 'value': 'speedboat'},
                        {'text': 'Shikaraboat 🛶', 'value': 'shikaraboat'}
                    ],
                    'new_state': 'select_boat_type',
                    'booking_details': booking_details
                }

            elif conversation_state == 'select_boat_type':
                if user_input in ['houseboat', 'motorboat', 'speedboat', 'shikaraboat']:
                    boat_name = user_input.title()
                    booking_details['selected_type'] = boat_name
                    booking_details['selected_boat_type'] = boat_name 
                    
                    response_data = {
                        'response': f"Excellent choice, a *{boat_name}! When would you like to book? Please select a **from date* and a *to date* on the calendar.",
                        'type': 'calendar',
                        'new_state': 'select_date',
                        'booking_details': booking_details
                    }
                else:
                    response_data = {
                        'response': "Please select one of the boat types.",
                        'options': [
                            {'text': 'Houseboat 🏠', 'value': 'houseboat'},
                            {'text': 'Motorboat 🚤', 'value': 'motorboat'},
                            {'text': 'Speedboat 🚀', 'value': 'speedboat'},
                            {'text': 'Shikaraboat 🛶', 'value': 'shikaraboat'}
                        ],
                        'new_state': 'select_boat_type',
                        'booking_details': booking_details
                    }

            # CHANGE: Calculate duration automatically and proceed to collect name
            elif conversation_state == 'select_date':
                booking_details['selected_date'] = user_input
                
                # --- NEW LOGIC: Calculate Duration ---
                duration_message = ''
                final_duration = '1 day'
                
                try:
                    # Input is a string like 'YYYY-MM-DD to YYYY-MM-DD'
                    start_date_str, end_date_str = user_input.split(' to ')
                    
                    # Parse dates
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    
                    # Calculate difference in days (adding 1 to include the last day)
                    duration = (end_date - start_date).days + 1 
                    
                    final_duration = f"{duration} days"
                    booking_details['duration'] = final_duration
                    duration_message = f" for *{final_duration}*"
                except Exception as e:
                    # In case of parsing error, store default value
                    print(f"Error parsing dates for duration calculation: {e}")
                    booking_details['duration'] = final_duration
                # --- END NEW LOGIC ---
                
                response_data = {
                    'response': f"Thank you! You've selected the date range *{user_input}*{duration_message}. What is your full name?",
                    'type': 'text_input',
                    'new_state': 'collect_name',
                    'booking_details': booking_details
                }
            
            # NOTE: The 'collect_duration' state has been entirely removed.

            elif conversation_state == 'collect_name':
                booking_details['name'] = user_input.title()
                response_data = {
                    'response': f"Thank you, {booking_details['name']}. What is your phone number?",
                    'type': 'text_input',
                    'new_state': 'collect_phone',
                    'booking_details': booking_details
                }

            elif conversation_state == 'collect_phone':
                booking_details['phone_number'] = user_input

                final_boat_type = booking_details.get('selected_type', 'N/A')
                final_dates = booking_details.get('selected_date', 'N/A')
                final_duration = booking_details.get('duration', 'N/A') # Retrieve calculated duration
                
                # === SEND EMAIL ===
                try:
                    subject = 'New Backwater Trip Booking Request'
                    message = (
                        f"A new boat booking request has been submitted.\n\n"
                        f"Name: {booking_details.get('name', 'N/A')}\n"
                        f"Phone Number: {booking_details.get('phone_number', 'N/A')}\n"
                        f"Boat Type: {final_boat_type}\n"
                        f"Booking Dates: {final_dates}\n"
                        f"Duration: {final_duration}" # INCLUDED: Calculated duration
                    )
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = ['primekeralacruise@gmail.com']

                    send_mail(subject, message, from_email, recipient_list)

                except Exception as e:
                    print(f"Error sending email: {e}") 

                # === SEND WHATSAPP MESSAGE VIA TWILIO ===
                try:
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

                    whatsapp_message = (
                        f"📌 New Backwater Boat Booking Request\n\n"
                        f"👤 Name: {booking_details.get('name', 'N/A')}\n"
                        f"📞 Phone: {booking_details.get('phone_number', 'N/A')}\n"
                        f"🚤 Type: {final_boat_type}\n"
                        f"📅 Dates: {final_dates}\n"
                        f"⏳ Duration: {final_duration}" # INCLUDED: Calculated duration
                    )
                    
                    client.messages.create(
                        body=whatsapp_message,
                        from_=settings.TWILIO_WHATSAPP_FROM,
                        to=settings.BUSINESS_WHATSAPP
                    )
                    Bookingcount.objects.create()
                except Exception as e:
                    print(f"Error sending WhatsApp message: {e}")

                # === FINAL BOT RESPONSE WITH "BOOK AGAIN" OPTION ===
                final_response = "✅ Thank you for the details! Here is your booking summary:\n"
                final_response += f"🚤 Boat Type: {final_boat_type}\n"
                final_response += f"📅 Booking Dates: {final_dates}\n"
                final_response += f"⏳ Duration: {final_duration}\n" # INCLUDED: Calculated duration
                final_response += f"👤 Name: {booking_details.get('name', 'N/A')}\n"
                final_response += f"📞 Phone Number: {booking_details.get('phone_number', 'N/A')}\n"
                final_response += "\nWe have received your request and will contact you to confirm your booking."

                response_data = {
                    'response': final_response,
                    'type': 'final',
                    'new_state': 'end',
                    'booking_details': {}, 
                    'options': [
                        {'text': 'Book Again 🔄', 'value': 'restart'}
                    ]
                }

            elif conversation_state == 'end':
                if user_input == 'restart':
                    booking_details = {} 
                    response_data = {
                        'response': "👋 Welcome back! What type of boat would you like to book?",
                        'options': [
                            {'text': 'Houseboat 🏠', 'value': 'houseboat'},
                            {'text': 'Motorboat 🚤', 'value': 'motorboat'},
                            {'text': 'Speedboat 🚀', 'value': 'speedboat'},
                            {'text': 'Shikaraboat 🛶', 'value': 'shikaraboat'}
                        ],
                        'new_state': 'select_boat_type',
                        'booking_details': booking_details
                    }
                else:
                    response_data = {
                        'response': "Your booking is complete. Tap 'Book Again' if you want to make another booking.",
                        'options': [
                            {'text': 'Book Again 🔄', 'value': 'restart'}
                        ],
                        'new_state': 'end',
                        'booking_details': booking_details
                    }

            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            # Catch all exceptions for robust error handling
            return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)



def admin_add_destination(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    if request.method == "POST":
        name = request.POST.get('name')
        photo = request.FILES.get('photo')  # important for image uploads

        if name and photo:
            destination = Destination(name=name, photo=photo)
            destination.save()
            return redirect('admin_view_destination')  # Redirect after saving

    return render(request, 'admin/admin_add_destination.html')


def admin_view_destination(request):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    destinations = Destination.objects.all()  # Get all rows
    return render(request, 'admin/admin_view_destinations.html', {'destinations': destinations})

def admin_edit_destination(request, id):
    if request.session['log']=="out":
        return HttpResponse(f"<script>alert('You havent logged in yet...!');window.location='/login'</script>")
    destination = Destination.objects.get(id=id)

    if request.method == "POST":
        name = request.POST.get('name')
        photo = request.FILES.get('photo')

        if name:
            destination.name = name
        if photo:
            destination.photo = photo

        destination.save()
        return redirect('admin_view_destination')  # Redirect to the list page after update

    return render(request, 'admin/admin_edit_destination.html', {'destination': destination})

def admin_delete_destination(request, id):
    Destination.objects.get(id=id).delete()
    return redirect('admin_view_destinations')



def changepassword(request):
    if 'lid' not in request.session:
        messages.error(request, "You must log in first.")
        return redirect('login')  # adjust as per your login URL name

    lid = request.session['lid']
    login_data = Login.objects.get(id=lid)

    if request.method == 'POST':
        cpass = request.POST['cpass']
        npass = request.POST['npass']
        confirmpass = request.POST['confirmpass']

        # Step 1: Check if current password matches
        if login_data.password != cpass:
            messages.error(request, "Current password is incorrect.")
            return redirect('changepassword')

        # Step 2: Confirm new password match
        if npass != confirmpass:
            messages.error(request, "New passwords do not match.")
            return redirect('changepassword')

        # Step 3: Update password
        login_data.password = npass
        login_data.save()

        messages.success(request, "Password changed successfully.")
        return redirect('changepassword')

    return render(request, 'admin/changepassword.html')



def admin_view_tariff(request):
    if request.session.get('log') == "out":
        return HttpResponse("<script>alert('You haven’t logged in yet...!');window.location='/login'</script>")

    # Fetch all tariffs ordered by type & category
    tariffs = Tariff1.objects.all().order_by('type', 'category')

    # Separate them by type for grouped display
    day_tariffs = tariffs.filter(type="DayCruise")
    night_tariffs = tariffs.filter(type="OvernightCruise")

    context = {
        'day_tariffs': day_tariffs,
        'night_tariffs': night_tariffs,
    }
    return render(request, 'admin/admin_view_tariff.html', context)


def admin_add_tariff(request):
    if request.method == "POST":
        category = request.POST.get("category")
        type = request.POST.get("type")

        if type == "DayCruise":
            base_people = request.POST.get("base_people")
            amount = request.POST.get("amount")
            extra_person_amount = request.POST.get("extra_person_amount")

            Tariff1.objects.create(
                category=category,
                type=type,
                base_people=base_people or None,
                amount=amount or None,
                extra_person_amount=extra_person_amount or None
            )

        elif type == "OvernightCruise":
            room_count = request.POST.get("room_count")
            amount = request.POST.get("amount_night")
            extra_person_charge = request.POST.get("extra_person_charge")
            note = request.POST.get("note")

            Tariff1.objects.create(
                category=category,
                type=type,
                room_count=room_count or None,
                amount=amount or None,
                extra_person_charge=extra_person_charge or None,
                note=note
            )

        return redirect("admin_view_tariff")

    return render(request, 'admin/admin_add_tariff.html')

def admin_delete_tariff(request, id):
    tariff = Tariff1.objects.get(id=id)
    tariff.delete()
    return redirect('admin_view_tariff')


def admin_edit_tariff(request, id):
    if request.session.get('log') == "out":
        return HttpResponse("<script>alert('You haven’t logged in yet...!');window.location='/login'</script>")

    tariff = Tariff1.objects.get(id=id)

    if request.method == "POST":
        tariff.category = request.POST.get("category")
        tariff.type = request.POST.get("type")

        if tariff.type == "DayCruise":
            tariff.amount = request.POST.get("amount") or None
            tariff.base_people = request.POST.get("base_people") or None
            tariff.extra_person_amount = request.POST.get("extra_person_amount") or None

            # Clear overnight-specific fields to avoid confusion
            tariff.room_count = None
            tariff.extra_person_charge = None
            tariff.note = None

        elif tariff.type == "OvernightCruise":
            tariff.room_count = request.POST.get("room_count") or None
            tariff.amount = request.POST.get("amount_night") or None
            tariff.extra_person_charge = request.POST.get("extra_person_charge") or None
            tariff.note = request.POST.get("note") or None

            # Clear day-specific fields
            tariff.base_people = None
            tariff.extra_person_amount = None

        tariff.save()
        return redirect("admin_view_tariff")

    return render(request, 'admin/admin_edit_tariff.html', {'tariff': tariff})




def admin_view_menu_items(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'admin/admin_view_menu.html', {'menu_items': menu_items})


def admin_add_menu_item(request):
    if request.method == 'POST':
        cruise_type = request.POST.get('cruise_type')
        package_type = request.POST.get('package_type')
        item_name = request.POST.get('item_name')
        details = request.POST.get('details', '')
        # time_slot = request.POST.get('time_slot', '')
        duration = request.POST.get('duration', '')
        ac_available = request.POST.get('ac_info')
        is_special = request.POST.get('special_info')
        image = request.FILES.get('image')
        order_number = request.POST.get('order_number') or 0

        MenuItem.objects.create(
            cruise_type=cruise_type,
            package_type=package_type,
            item_name=item_name,
            details=details,
            duration=duration,
            ac_available=ac_available,
            is_special=is_special,
            image=image,
            order_number=int(order_number),
        )
        return redirect('admin_view_menu_items')  # change to your list-view name

    # GET -> show empty form (you can pass previous form values if editing)
    return render(request, 'admin/admin_add_menu.html')

def admin_delete_menu(request, id):
    menu = MenuItem.objects.get(id=id)
    menu.delete()
    return redirect('admin_view_menu_items')


def admin_edit_menu_item(request, id):
    # Fetch the item or show 404 if not found
    menu_item = get_object_or_404(MenuItem, id=id)

    if request.method == 'POST':
        # Get all form data
        cruise_type = request.POST.get('cruise_type')
        package_type = request.POST.get('package_type')
        item_name = request.POST.get('item_name')
        details = request.POST.get('details')
        # time_slot = request.POST.get('time_slot')
        duration = request.POST.get('duration')
        ac_available = request.POST.get('ac_available')
        is_special = request.POST.get('is_special')
        order_number = request.POST.get('order_number') or 0
        image = request.FILES.get('image')

        # Update fields
        menu_item.cruise_type = cruise_type
        menu_item.package_type = package_type
        menu_item.item_name = item_name
        menu_item.details = details
        # menu_item.time_slot = time_slot
        menu_item.duration = duration
        menu_item.ac_available = ac_available
        menu_item.is_special = is_special
        menu_item.order_number = order_number

        # Update image only if a new one is uploaded
        if image:
            menu_item.image = image

        # Save the updated record
        menu_item.save()

        # Show confirmation message
        messages.success(request, f"✅ '{menu_item.item_name}' updated successfully.")
        return redirect('admin_view_menu_items')  # Change this to your view list URL name

    return render(request, 'admin/admin_edit_menu.html', {'menu_item': menu_item})



def admin_view_all_bookings(request):
    package_bookings = PackageBooking.objects.all().order_by('-created_at')
    boat_bookings = BoatBooking.objects.all().order_by('-created_at')

    context = {
        'package_bookings': package_bookings,
        'boat_bookings': boat_bookings,
    }
    return render(request, 'admin/view_all_bookings.html', context)    



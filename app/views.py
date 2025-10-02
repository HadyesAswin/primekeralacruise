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

from datetime import datetime
# Create your views here.


# -----------------------------------Public functions----------------------------------

def index(request):
    boats = Boat.objects.all()[:4]
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
def index1(request):
   
 # show only 6 packages
    return render(request, 'public/index1.html', 
        )

def login(request):
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

# -----------------------------------User functions----------------------------------

def packages(request):
    packages = Package.objects.all()

    return render(request,'user/packages.html', {'packages': packages})
# def package_detail(request, pk):
#     package = get_object_or_404(Package, pk=pk)
#     return render(request, 'user/package_detail.html', {'package': package})

def boats(request):
    boats = Boat.objects.all()

    return render(request,'user/boats.html', {'boats': boats})
# def gallery(request):
#     photos = Gallery.objects.all()

#     return render(request,'user/gallery.html', {'photos': photos})

# def aboutus(request):
#     return render(request,'user/aboutus.html')




def allpackages(request):
    packages = Package.objects.all()
    paginator = Paginator(packages, 6)  # Show 6 packages per page
    page_number = request.GET.get('page')  # ?page=2
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'public/allpackages.html', {'page_obj': page_obj})

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
    now = timezone.now()
    one_week_ago = now - timedelta(days=7)
    one_month_ago = now - timedelta(days=30)

    # Count rows where booking_count datetime is within the range
    weekly_count = Bookingcount.objects.filter(booking_count__gte=one_week_ago).count()
    monthly_count = Bookingcount.objects.filter(booking_count__gte=one_month_ago).count()

    counts = {'weekly': weekly_count, 'monthly': monthly_count}
    return render(request, 'admin/admin_home.html', {'counts': counts})

def admin_view_package(request):
    packages = Package.objects.all()
    return render(request, 'admin/admin_view_package.html', {'packages': packages})

def admin_add_package(request):
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
    package = Package.objects.get(id=id)
    if request.method == 'POST':
        package.title = request.POST.get('title')
        package.description = request.POST.get('description')
        package.price = request.POST.get('price')
        package.duration = request.POST.get('duration')
        package.noofperson = request.POST.get('person')
        if 'photo' in request.FILES:
            package.photo = request.FILES['photo']
        package.save()
        return redirect('admin_view_package')
    return render(request, 'admin/admin_edit_package.html', {'package': package})

def admin_delete_package(request, id):
    package = Package.objects.get(id=id)
    package.delete()
    return redirect('admin_view_package')

def admin_add_boat(request):
    if request.method == 'POST':
        price = request.POST.get('price')
        photo = request.FILES.get('photo')
        description = request.POST.get('description')
        category = request.POST.get('category')
        Boat.objects.create(
            price=price,
            photo=photo,
            description=description,
            category=category
        )
        return redirect('admin_view_boat')
    return render(request, 'admin/admin_add_boat.html')

def admin_view_boat(request):
    boats = Boat.objects.all()
    return render(request, 'admin/admin_view_boat.html', {'boats': boats})

def admin_edit_boat(request, id):
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

def admin_view_room(request):
    rooms = Room.objects.all()
    return render(request, 'admin/admin_view_room.html', {'rooms': rooms})

def admin_add_room(request):
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
    photos = Gallery.objects.all()
    return render(request, 'admin/admin_view_gallery.html', {'photos': photos})

def admin_add_gallery(request):
    if request.method == "POST":
        photo = request.FILES.get('photo')
        if photo:
            Gallery.objects.create(photo=photo)
            return redirect('admin_view_gallery')
    return render(request, 'admin/admin_add_gallery.html')

def admin_edit_gallery(request, id):
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
    testimonials = Testimonial.objects.all()
    return render(request, 'admin/admin_view_testimonial.html', {'testimonials': testimonials})

def admin_add_testimonial(request):
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
                final_duration = '1 day (Date calculation error)'
                
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
                    recipient_list = ['etournament49@gmail.com']

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
    if request.method == "POST":
        name = request.POST.get('name')
        photo = request.FILES.get('photo')  # important for image uploads

        if name and photo:
            destination = Destination(name=name, photo=photo)
            destination.save()
            return redirect('admin_view_destination')  # Redirect after saving

    return render(request, 'admin/admin_add_destination.html')

def admin_view_destination(request):
    destinations = Destination.objects.all()  # Get all rows
    return render(request, 'admin/admin_view_destinations.html', {'destinations': destinations})

def admin_edit_destination(request, id):
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











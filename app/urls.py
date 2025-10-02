from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [

    #--------------Public-----------------
    path('',views.index),
    path('kh',views.index1),

    path('login',views.login),
    #--------------User-----------------

    path('packages',views.packages,name='packages'),
    # path('package/<int:pk>/', views.package_detail, name='package_detail'),

    path('boats',views.boats,name='boats'),
    # path('boat/<int:pk>/', views.boat_detail, name='boat_detail'),

    # path('gallery',views.gallery,name='gallery'),
    # path('aboutus',views.aboutus,name='aboutus'),
    path('allpackages',views.allpackages,name='allpackages'),
    path('allboats',views.allboats,name='allboats'),
    path('alldestinations',views.alldestinations,name='alldestinations'),
    path('aboutus',views.aboutus,name='aboutus'),
    path('allgallery',views.allgallery,name='allgallery'),

    #--------------Admin-----------------
    path('admin_home',views.admin_home),
    path('admin_view_package',views.admin_view_package, name='admin_view_package'),
    path('admin_add_package',views.admin_add_package,name='admin_add_package'),
    path('admin_edit_package/<int:id>',views.admin_edit_package, name='admin_edit_package'),
    path('admin_delete_package/<int:id>',views.admin_delete_package, name='admin_delete_package'),
    path('admin_view_boat',views.admin_view_boat,name='admin_view_boat'),
    path('admin_add_boat',views.admin_add_boat,name='admin_add_boat'),
    path('admin_edit_boat/<int:id>',views.admin_edit_boat,name='admin_edit_boat'),
    path('admin_delete_boat/<int:id>',views.admin_delete_boat,name='admin_delete_boat'),
    path('admin_view_room',views.admin_view_room, name='admin_view_room'),
    path('admin_add_room',views.admin_add_room,name='admin_add_room'),
    path('admin_edit_room/<int:id>',views.admin_edit_room,name='admin_edit_room'),
    path('admin_delete_room/<int:id>',views.admin_delete_room,name='admin_delete_room'),
    path('admin_view_gallery',views.admin_view_gallery, name='admin_view_gallery'),
    path('admin_add_gallery',views.admin_add_gallery,name='admin_add_gallery'),
    path('admin_edit_gallery/<int:id>',views.admin_edit_gallery,name='admin_edit_gallery'),
    path('admin_delete_gallery/<int:id>',views.admin_delete_gallery,name='admin_delete_gallery'),
    path('admin_view_testimonial',views.admin_view_testimonial, name='admin_view_testimonial'),
    path('admin_add_testimonial',views.admin_add_testimonial,name='admin_add_testimonial'),
    path('admin_edit_testimonial/<int:id>',views.admin_edit_testimonial,name='admin_edit_testimonial'),
    path('admin_delete_testimonial/<int:id>',views.admin_delete_testimonial,name='admin_delete_testimonial'),

    path('chatbot-api/', views.chatbot_api, name='chatbot-api'),
    path('admin_add_destination/', views.admin_add_destination, name='admin_add_destination'),
    path('admin_view_destination', views.admin_view_destination, name='admin_view_destination'),
    path('admin_edit_destination/<int:id>', views.admin_edit_destination, name='admin_edit_destination'),
    path('admin_delete_destination/<int:id>', views.admin_delete_destination, name='admin_delete_destination'),
    # path('admin_view_booking_count',views.admin_view_booking_count,name='admin_view_booking_count'),
]

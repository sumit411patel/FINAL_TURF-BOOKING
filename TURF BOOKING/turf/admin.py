from django.contrib import admin
from .models import *
# Register your models here.

admin.site.site_header = "Turf Booking Admin"

class users(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'password', 'phone_number', 'user_type']
    

admin.site.register(login,users)


class display_user_details(admin.ModelAdmin):
    list_display = ['id', 'user', 'address', 'profile_photo', 'dob']


admin.site.register(user_detail, display_user_details)


class displaystate(admin.ModelAdmin):

    list_display = ['state_name']

admin.site.register(state,displaystate)


class displaycity(admin.ModelAdmin):
    list_display = ['state_name', 'city_name']


admin.site.register(city,displaycity)


class displaylocation (admin.ModelAdmin):
    list_display = ['city_name', 'area_name', 'postal_code']


admin.site.register(location, displaylocation)


class display_turf_categories(admin.ModelAdmin):
    list_display = ['id', 'cate_name']


admin.site.register(turf_categories ,display_turf_categories)


class displayturf (admin.ModelAdmin):
    list_display = ['manager', 'category', 'location', 'name', 'description', 'contact_number', 'contact_email', 'price_per_slot', 'maximum_capacity', 'is_available', 'rules_and_regulations']


admin.site.register(turf, displayturf)





class displayslot(admin.ModelAdmin):
    list_display = ['turf','date', 'start_time', 'end_time', 'is_booked', 'is_available']


admin.site.register(slot, displayslot)


class displaybookings(admin.ModelAdmin):
    list_display = ['user', 'turf', 'slot', 'booking_status', 'booked_at']


admin.site.register(booking,displaybookings)


class displaypayment(admin.ModelAdmin):
    list_display = ['user', 'booking', 'amount', 'payment_method', 'transaction_id', 'payment_date_time', 'payment_status']


admin.site.register(payment,displaypayment)



class displayfeedback(admin.ModelAdmin):
    list_display = ['user', 'turf', 'comment', 'rating', 'timestamp']


admin.site.register(feedback, displayfeedback)

class displayinquiry(admin.ModelAdmin):
    list_display = ['name', 'contact_number', 'contact_email', 'subject', 'description', 'status', 'timestamp']


admin.site.register(inquiry, displayinquiry)



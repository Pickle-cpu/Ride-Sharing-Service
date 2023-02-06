from django.contrib import admin
from .models import UserProfile, Car, Ride
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Car)
admin.site.register(Ride)
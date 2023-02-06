from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserProfile(models.Model):
    user = models.CharField(default = "", primary_key = True, max_length = 150)
    isDriver = models.IntegerField(default = 0)

    def __str__(self):
        return self.user

class RideSharer(models.Model):
    sharerridepk = models.IntegerField(default = 0)
    sharerName = models.CharField(default = "", max_length = 150)
    numPassengers = models.IntegerField(default = 1)

class Car(models.Model):
    driverName = models.CharField(default = "", max_length = 150)
    carType = models.CharField(default = "sedan", max_length=20)
    maxCapacity = models.IntegerField(default = 4)
    licensePlateNumber = models.CharField(default = "", max_length=10)
    driverspecialRequest = models.CharField(default="", max_length = 300)
    
class RideCar(models.Model):
    driverName = models.CharField(default = "", max_length = 150)
    carType = models.CharField(default = "sedan", max_length=20)
    maxCapacity = models.IntegerField(default = 4)
    licensePlateNumber = models.CharField(default = "", max_length=10)
    driverspecialRequest = models.CharField(default="", max_length = 300)

class Ride(models.Model):
    start = models.CharField(max_length = 100)
    destination = models.CharField(max_length = 100)
    arrivalTime = models.DateTimeField()
    SHARESTATUS = (('shareable', 'shareable'),
                    ('private', 'private'))
    isSharing = models.CharField(choices = SHARESTATUS,max_length = 20)
    ownerName = models.CharField(default = "",max_length = 150) 
    driverName = models.CharField(default = "",max_length = 150) 
    ridecar = models.ForeignKey(RideCar, blank = True, on_delete = models.CASCADE, related_name = 'ridecar')
    ridesharer = models.ManyToManyField(RideSharer, blank = True, related_name = 'ridesharer')
    specialRequest = models.CharField(default="", max_length = 300)
    cartypeRequest = models.CharField(default = "sedan", max_length=20)
    
    # rideStatus : open, confirmed, complete
    rideStatus = models.CharField(default='open',max_length = 20)
    
    ridesharercount = models.IntegerField(default = 0)
    
    def __str__(self):
        return f'From {self.start} to {self.destination}, arrive at {self.arrivalTime}. status: {self.rideStatus}'

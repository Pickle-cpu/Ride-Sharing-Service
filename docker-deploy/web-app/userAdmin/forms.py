from django import forms
from .models import User, RideSharer, UserProfile, Car, Ride
from django.utils import formats

class MySplitDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets = [forms.SelectDateWidget(), forms.TimeInput()]


class DriverRegisterForm(forms.ModelForm):
    carType = forms.CharField()
    maxCapacity = forms.IntegerField(required = False)
    licensePlateNumber = forms.CharField()
    driverspecialRequest = forms.CharField()
    class Meta:
        model = Car
        fields = ['carType','maxCapacity','licensePlateNumber','driverspecialRequest']

class UserProfileUpdateForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)
    email = forms.EmailField()
    

class RideRequestUpdateForm(forms.ModelForm):
    SHARESTATUS = (('shareable', 'shareable'),
                    ('private', 'private'))

    start = forms.CharField(max_length = 100)
    destination = forms.CharField(max_length = 100)
    arrivalTime = forms.DateTimeField()
    isSharing = forms.CharField(widget = forms.Select(choices = SHARESTATUS))
    specialRequest = forms.CharField(required = False)
    cartypeRequest = forms.CharField(required = False) 
    class Meta:
        model = Ride
        fields = ['start','destination','arrivalTime','isSharing','specialRequest','cartypeRequest']

class RideSharerSearchForm(forms.Form):

    sharerDestination = forms.CharField(max_length = 100)
    earliestarrivalTime = forms.DateTimeField()
    latestarrivalTime = forms.DateTimeField()
    numPassengers = forms.IntegerField()

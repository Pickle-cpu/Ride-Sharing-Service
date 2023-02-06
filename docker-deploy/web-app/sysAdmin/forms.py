from django import forms
from userAdmin.models import User
from userAdmin.models import UserProfile, Car, Ride
from django.contrib.auth.forms import UserCreationForm
class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','password']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username','email','password1','password2']   



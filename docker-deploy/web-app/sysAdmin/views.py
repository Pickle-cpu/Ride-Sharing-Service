from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.http import Http404
from django.urls import reverse
from datetime import datetime, timedelta
from django.contrib import auth
from userAdmin.models import User,UserProfile, Car, Ride
from sysAdmin.forms import UserRegisterForm

# Create your views here.

def register(request):
    errors = []
    username = None
    password1 = None
    password2 = None
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if not username:
                errors.append('please enter username!')
            if not password1:
                errors.append('please enter password!')
            if not password2:
                errors.append('please enter password again!')
            if password1 and password2:
                if password1 == password2:
                    form.save()
                    user = User.objects.get(username=username)
                    userProfile = UserProfile(user=user,isDriver=0)
                    userProfile.save()
                    
                    return redirect('login')
                else:
                    errors.append('please repeat the password!')        
    else:
        form = UserRegisterForm()
    return render(request, 'register.html',{'form':form})


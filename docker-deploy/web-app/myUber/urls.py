"""myUber URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from sysAdmin import views as sysviews
from userAdmin import views as userviews

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'),name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('accounts/register/', sysviews.register, name='register'),
    path('user/driverCancel/', userviews.driverCancel, name = 'driverCancel'),
    path('user/driverRegister/', userviews.driverRegister, name = 'driverRegister'),
    path('user/profile/', userviews.profile, name = 'profile'),
    path('ride/rideRequest/',userviews.rideRequest, name = 'rideRequest'),
    path('ride/rideViewing/',userviews.rideViewing, name = 'rideViewing'),
    #path('ride/rideViewing/rideEditOwner/<int:ride_id>/',userviews.rideRequestEditOwner, name = 'rideEdit'),
    path('ride/rideEditOwner/<int:ride_id>/',userviews.rideRequestEditOwner, name = 'rideEdit1'),
    path('ride/rideBrowseOwnerOpen/rideEditOwner/<int:ride_id>/',userviews.rideRequestEditOwner, name = 'rideEdit2'),
    #path('ride/rideViewing/ride/rideComplete/<int:ride_id>/',userviews.rideComplete, name = 'rideComplete'),
    path('ride/rideComplete/<int:ride_id>/',userviews.rideComplete, name = 'rideComplete1'),
    path('ride/rideBrowseDriverConfirmed/ride/rideComplete/<int:ride_id>/',userviews.rideComplete, name = 'rideComplete2'),
    path('ride/rideStart/',userviews.rideStart, name = 'rideStart'),
    path('ride/rideSearch/',userviews.rideSearch, name = 'rideSearch'),
    path('ride/rideSharerSearch/',userviews.rideSharerSearch, name = 'rideSharerSearch'),
    path('ride/rideSharerSearchResult/',userviews.rideSharerSearchResult, name = 'rideSharerSearchResult'),
    #path('ride/rideViewing/rideEditSharer/<int:ride_id>/',userviews.rideRequestEditSharer, name = 'rideEditSharer'),
    path('ride/rideEditSharer/<int:ride_id>/',userviews.rideRequestEditSharer, name = 'rideEditSharer1'),
    path('ride/rideBrowseSharerOpen/rideEditSharer/<int:ride_id>/',userviews.rideRequestEditSharer, name = 'rideEditSharer2'),
    path('ride/rideBrowseOwnerOpen/',userviews.rideBrowseOwnerOpen, name = 'rideBrowseOwnerOpen'),
    path('ride/rideBrowseOwnerConfirmed/',userviews.rideBrowseOwnerConfirmed, name = 'rideBrowseOwnerConfirmed'),
    path('ride/rideBrowseOwnerCompleted/',userviews.rideBrowseOwnerCompleted, name = 'rideBrowseOwnerCompleted'),
    path('ride/rideBrowseDriverConfirmed/',userviews.rideBrowseDriverConfirmed, name = 'rideBrowseDriverConfirmed'),
    path('ride/rideBrowseDriverCompleted/',userviews.rideBrowseDriverCompleted, name = 'rideBrowseDriverCompleted'),
    path('ride/rideBrowseSharerOpen/',userviews.rideBrowseSharerOpen, name = 'rideBrowseSharerOpen'),
    path('ride/rideBrowseSharerConfirmed/',userviews.rideBrowseSharerCompleted, name = 'rideBrowseSharerConfirmed'),
    path('ride/rideBrowseSharerCompleted/',userviews.rideBrowseSharerCompleted, name = 'rideBrowseSharerCompleted'),
]

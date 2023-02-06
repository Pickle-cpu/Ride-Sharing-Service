from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.http import Http404
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from userAdmin.models import User, UserProfile, RideSharer, Car, RideCar, Ride
from sysAdmin.forms import UserRegisterForm
from userAdmin.forms import DriverRegisterForm, UserProfileUpdateForm, RideRequestUpdateForm, RideSharerSearchForm
from django.db.models import Count
from django.core.mail import send_mail
# from django.contrib.staticfiles.templatetags.staticfiles import static
# Create your views here.

@login_required
def driverRegister(request):
    userprofile = UserProfile.objects.get(user = request.user.username)
    if(userprofile.isDriver==1):
        context = {'prompt':'Every user can only register one car!'}
        return render(request,'home.html',context)
    if request.method == 'POST':
        form = DriverRegisterForm(request.POST)
        if(userprofile.isDriver==1):
            return redirect('home')
        if form.is_valid():
    
            userprofile.isDriver = 1
            userprofile.save()

            driverName = request.user.username
            carType = form.cleaned_data.get('carType')
            maxCapacity = form.cleaned_data.get('maxCapacity')
            licensePlateNumber = form.cleaned_data.get('licensePlateNumber')
            driverspecialRequest = form.cleaned_data.get('driverspecialRequest')
            car = Car(driverName = driverName, carType = carType, maxCapacity = maxCapacity, licensePlateNumber = licensePlateNumber, driverspecialRequest = driverspecialRequest)
            car.save()

            context = {'prompt':"successfully register, enjoy driving!"}
            return render(request,'home.html',context)
    else:
        form = DriverRegisterForm()
    return render(request,'driverRegister.html',{'form':form})

@login_required
def driverCancel(request):
    # 如果有未完成的ride不能取消 后续加上
    currentRide = list(Ride.objects.filter(driverName = request.user.username))
    if currentRide:
        context = {'prompt':'Please finish your ride!'}
        return render(request,'home.html',context)
    context = {'prompt':'You are no longer a driver!'}
    userProfile = UserProfile.objects.get(user = request.user.username)
    if userProfile.isDriver == 0:
        return render(request,'home.html',context)
    else:
        car = Car.objects.get(driverName = request.user.username)
        car.delete()
        
        userProfile.isDriver = 0
        userProfile.save()
    return render(request,'home.html',context)

@login_required
def profile(request):
    userProfile = UserProfile.objects.get(user=request.user.username)
    if request.method == 'POST':

        profileUpdateForm = UserProfileUpdateForm(request.POST)
        driverUpdateForm = DriverRegisterForm()
        if userProfile.isDriver==1:
            driverUpdateForm = DriverRegisterForm(request.POST)
    
        # update profile
        if profileUpdateForm.is_valid():
            username = profileUpdateForm.cleaned_data.get('username')
            email = profileUpdateForm.cleaned_data.get('email')
            password = profileUpdateForm.cleaned_data.get('password')
            password=make_password(password,hasher='default')
            if username != request.user.username:
                # update all relative data
                UserProfile.objects.filter(user=request.user.username).update(user = username)
                RideSharer.objects.filter(sharerName = request.user.username).update(sharerName = username)
                Car.objects.filter(driverName = request.user.username).update(driverName = username)
                RideCar.objects.filter(driverName = request.user.username).update(driverName = username)
                Ride.objects.filter(ownerName = request.user.username).update(ownerName = username)
                Ride.objects.filter(driverName = request.user.username).update(driverName = username)
            User.objects.filter(id=request.user.id).update(username = username,email = email,password = password)

            if userProfile.isDriver==1:
                car = Car.objects.get(driverName=username)
                driverUpdateForm = DriverRegisterForm(instance=car)
            context = {'profileUpdateForm':profileUpdateForm,'driverUpdateForm':driverUpdateForm,'prompt':"successfully update profile!"}
            return render(request,'home.html',context)

        if driverUpdateForm.is_valid():
            profileUpdateForm = UserProfileUpdateForm()
            carType = driverUpdateForm.cleaned_data.get('carType')
            maxCapacity = driverUpdateForm.cleaned_data.get('maxCapacity')
            # exception: negative capacity
            if(maxCapacity<=0):
                driverUpdateForm = DriverRegisterForm(instance=car)
                context = {'profileUpdateForm':profileUpdateForm,'driverUpdateForm':driverUpdateForm,'prompt':"please select valid capacity!"}
                return render(request,'profile.html',context)
            licensePlateNumber = driverUpdateForm.cleaned_data.get('licensePlateNumber')
            driverspecialRequest = driverUpdateForm.cleaned_data.get('driverspecialRequest')
            Car.objects.filter(driverName=request.user.username).update(driverName = request.user.username, carType = carType, maxCapacity = maxCapacity, licensePlateNumber = licensePlateNumber, driverspecialRequest = driverspecialRequest)
            RideCar.objects.filter(driverName=request.user.username).update(driverName = request.user.username, carType = carType, maxCapacity = maxCapacity, licensePlateNumber = licensePlateNumber, driverspecialRequest = driverspecialRequest)
            context = {'profileUpdateForm':profileUpdateForm,'driverUpdateForm':driverUpdateForm,'prompt':"successfully update car info!"}
            return render(request,'home.html',context)
       
    # display profile
    else:
        profileUpdateForm = UserProfileUpdateForm(initial = {'username' : request.user.username, 'email':request.user.email})
        driverUpdateForm = DriverRegisterForm()
        if(userProfile.isDriver==1):
            car = Car.objects.get(driverName=request.user.username)
            driverUpdateForm = DriverRegisterForm(instance=car)
    return render(request,'profile.html',{'profileUpdateForm':profileUpdateForm,'driverUpdateForm':driverUpdateForm,'isDriver':userProfile.isDriver})

@login_required
def rideRequest(request):
    # todo : what if a user request two similar rides?
    if request.method == 'POST':
        form = RideRequestUpdateForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data.get('start')
            destination = form.cleaned_data.get('destiniation')
            # compare time
            time = timezone.now()
            arrivalTime = form.cleaned_data.get('arrivalTime')
            if arrivalTime < time:
                return render(request,'home.html',{'prompt':"Ride request failed, please select correct time!"})
            isSharing = form.cleaned_data.get('isSharing')
            destination = form.cleaned_data.get('destination')
            ownerName = request.user.username
            specialRequest = form.cleaned_data.get('specialRequest')
            
            cartypeRequest = "sedan"
            if form.cleaned_data.get('cartypeRequest') != cartypeRequest:
                cartypeRequest = form.cleaned_data.get('cartypeRequest')
            # save inner first
            ridecar = RideCar()
            ridecar.save()
            ride = Ride(ridecar = ridecar, start = start, destination = destination, arrivalTime = arrivalTime, isSharing = isSharing, 
            ownerName = ownerName,  specialRequest = specialRequest, cartypeRequest = cartypeRequest)
            ride.save()
            context = {'prompt':"successfully request a ride!"}
            return render(request,'home.html',context)
    else:
        form = RideRequestUpdateForm()
    return render(request,'rideRequest.html',{'form':form})

@login_required
def rideViewing(request):
    ownerOpen = list(Ride.objects.filter(ownerName = request.user.username, rideStatus = 'open'))
    ownerConfirmed = list(Ride.objects.filter(ownerName = request.user.username, rideStatus = 'confirmed'))
    ownerCompleted = list(Ride.objects.filter(ownerName = request.user.username, rideStatus = 'completed'))
    
    driverConfirmed = list(Ride.objects.filter(driverName = request.user.username).filter(rideStatus='confirmed'))
    driverCompleted = list(Ride.objects.filter(driverName = request.user.username).filter(rideStatus='completed'))
    
    rideOpen = list(Ride.objects.filter(rideStatus='open'))
    sharerOpen = list()
    for ride in rideOpen:
        num = ride.ridesharer.all().filter(sharerName = request.user.username).count()
        if(num != 0):
            sharerOpen += (Ride.objects.filter(pk=ride.pk))
            
    rideConfirmed = list(Ride.objects.filter(rideStatus='confirmed'))
    sharerConfirmed = list()
    for ride in rideConfirmed:
        num = ride.ridesharer.all().filter(sharerName = request.user.username).count()
        if(num != 0):
            sharerConfirmed += (Ride.objects.filter(pk=ride.pk))
    
    rideCompleted = list(Ride.objects.filter(rideStatus='completed'))
    sharerCompleted = list()
    for ride in rideCompleted:
        num = ride.ridesharer.all().filter(sharerName = request.user.username).count()
        if(num != 0):
            sharerCompleted += (Ride.objects.filter(pk=ride.pk))
        
    return render(request,'rideView.html',{'ownerOpen':ownerOpen, 'ownerConfirmed':ownerConfirmed, 'ownerCompleted':ownerCompleted, 'driverConfirmed':driverConfirmed, 'driverCompleted':driverCompleted, 'driverCompleted':driverCompleted, 'sharerOpen':sharerOpen, 'sharerConfirmed':sharerConfirmed, 'sharerCompleted':sharerCompleted})


@login_required
def rideRequestEditOwner(request, ride_id):
    ride = get_object_or_404(Ride, id = ride_id)
    if request.method == 'POST':
        form = RideRequestUpdateForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data.get('start')
            destination = form.cleaned_data.get('destination')
            arrivalTime = form.cleaned_data.get('arrivalTime')
            isSharing = form.cleaned_data.get('isSharing')
            specialRequest = form.cleaned_data.get('specialRequest')
            cartypeRequest = form.cleaned_data.get('cartypeRequest')
            ride.start = start
            ride.destination = destination
            ride.arrivalTime = arrivalTime
            ride.isSharing = isSharing
            ride.specialRequest = specialRequest
            if cartypeRequest != '':
                ride.cartypeRequest = cartypeRequest
            ride.save()
            form = RideRequestUpdateForm()
            prompt = "Successfully update the ride"
            return redirect('rideViewing')
    else:
        form = RideRequestUpdateForm(instance = ride)
    return render(request, 'rideEditOwner.html',{'form':form})

@login_required
def rideComplete(request, ride_id):
    ride = get_object_or_404(Ride, id = ride_id)
    ride.rideStatus = "completed"
    ride.save()
    return redirect('home')

# ps : when driver confirm, you need to update the ride.car field in ride objects, as well as the drivername.

@login_required
def rideStart(request):
    return render(request,'rideStart.html')

@login_required
def rideSearch(request):
    userprofile = UserProfile.objects.get(user = request.user.username)
    if userprofile.isDriver == 0:
        context = {'prompt':"You are not a driver!"}
        return render(request,'home.html',context)
    if request.method == 'POST':
        
        chosenRide = Ride.objects.get(pk = request.POST['rideChosen'])
        chosenRide.rideStatus = "confirmed"
        chosenRide.driverName = request.user.username
        chosenRide.ridecar.driverName = request.user.username
        chosenRide.ridecar.carType = Car.objects.get(driverName = request.user.username).carType
        chosenRide.ridecar.maxCapacity = Car.objects.get(driverName = request.user.username).maxCapacity
        chosenRide.ridecar.licensePlateNumber = Car.objects.get(driverName = request.user.username).licensePlateNumber
        chosenRide.ridecar.driverspecialRequest = Car.objects.get(driverName = request.user.username).driverspecialRequest
        chosenRide.ridecar.save()
        chosenRide.save()
        
        emailaddress = User.objects.get(username = chosenRide.ownerName).email
        # send an email
        send_mail('Your ride is confirmed','Your ride is confirmed. Enjoy it!','zcgyxece568@outlook.com',[emailaddress])
        return redirect('home')
    
    cartypeRequest = Car.objects.get(driverName = request.user.username).carType
    maxCapacity = Car.objects.get(driverName = request.user.username).maxCapacity
    driverspecialRequest = Car.objects.get(driverName = request.user.username).driverspecialRequest
    
    ownerOpen = list(Ride.objects.filter(rideStatus = 'open', cartypeRequest = cartypeRequest).exclude(ownerName = request.user.username))
    rideSuitable = list()
    for ride in ownerOpen:
        if ride.ridesharer.all().count() <= maxCapacity - 1 or ride.ridesharer.all().count() == 0:
            # cannot be the sharer and driver at the same time
            namecount = ride.ridesharer.all().filter(sharerName = request.user.username).count()
            if namecount == 0:
                # special request of ride matches special request of driver if available
                if ride.specialRequest == driverspecialRequest or ride.specialRequest == '':
                    rideSuitable += (Ride.objects.filter(pk=ride.pk))
    return render(request,'rideSearch.html',{'rideSuitable':rideSuitable, 'cartypeRequest':cartypeRequest, 'maxCapacity':maxCapacity})

@login_required
def rideSharerSearch(request):

    if request.method == 'POST':
        form = RideSharerSearchForm(request.POST)
        if form.is_valid():

            sharerDestination = form.cleaned_data.get('sharerDestination')
            earliestarrivalTime = form.cleaned_data.get('earliestarrivalTime')
            latestarrivalTime = form.cleaned_data.get('latestarrivalTime')
            numPassengers = form.cleaned_data.get('numPassengers')
            # exception: negative capacity
            if(numPassengers<1):
                form = RideSharerSearchForm()
                context = {'prompt':"please select valid passenger number!"}
                return render(request,'rideSharerSearch.html',{'form':form, 'context':context})
            ownerOpen = list(Ride.objects.filter(rideStatus = 'open', isSharing = 'shareable', destination = sharerDestination).exclude(ownerName = request.user.username))
            rideSuitable = list()
            for ride in ownerOpen:
                if ride.ridecar.maxCapacity >= numPassengers + 1 and latestarrivalTime >= ride.arrivalTime and earliestarrivalTime <= ride.arrivalTime:
                    # can join a ride only once
                    namecount = ride.ridesharer.all().filter(sharerName = request.user.username).count()
                    if namecount == 0:
                        rideSuitable += (Ride.objects.filter(pk=ride.pk))
            form = RideSharerSearchForm()
            return render(request,'rideSharerSearch.html',{'form':form,'rideSuitable':rideSuitable,'numPassengers':numPassengers})
    else:
        form = RideSharerSearchForm()
    return render(request,'rideSharerSearch.html',{'form':form})

@login_required
def rideSharerSearchResult(request):
    
    if request.method == 'POST':
        chosenRide = Ride.objects.get(pk = request.POST['ridepk'])
        ridesharer = RideSharer(sharerridepk = request.POST['ridepk'], sharerName = request.user.username, numPassengers = request.POST['numPassengers'])
        ridesharer.save()
        chosenRide.ridesharer.add(ridesharer)
        chosenRide.ridesharercount += int(ridesharer.numPassengers)
        chosenRide.save()
    return render(request,'rideSharerSearchResult.html')

@login_required
def rideRequestEditSharer(request, ride_id):
    ride = get_object_or_404(Ride, id = ride_id)
    sharerLeave = ride.ridesharer.get(sharerName = request.user.username)
    sharerLeavepk = sharerLeave.sharerridepk
    ride.ridesharercount -= sharerLeave.numPassengers
    ride.ridesharer.remove(sharerLeave)
    ride.save()
    RideSharer.objects.get(sharerridepk = sharerLeavepk, sharerName = request.user.username).delete()
    return render(request,'rideRequestEditSharer.html')

@login_required
def rideBrowseOwnerOpen(request):
    ride = Ride()
    if request.method == 'POST':
        ride = Ride.objects.get(pk = request.POST['ridepk'])
        
    return render(request,'rideBrowseOwnerOpen.html',{'ride':ride})

@login_required
def rideBrowseOwnerConfirmed(request):
    ride = Ride()
    if request.method == 'POST':
        ride = Ride.objects.get(pk = request.POST['ridepk'])
        
    return render(request,'rideBrowseOwnerConfirmed.html',{'ride':ride})

@login_required
def rideBrowseOwnerCompleted(request):
    ride = Ride()
    if request.method == 'POST':
        ride = Ride.objects.get(pk = request.POST['ridepk'])
        
    return render(request,'rideBrowseOwnerCompleted.html',{'ride':ride})

@login_required
def rideBrowseDriverConfirmed(request):
    ride = Ride()
    if request.method == 'POST':
        ride = Ride.objects.get(pk = request.POST['ridepk'])
        
    return render(request,'rideBrowseDriverConfirmed.html',{'ride':ride})

@login_required
def rideBrowseDriverCompleted(request):
    ride = Ride()
    if request.method == 'POST':
        ride = Ride.objects.get(pk = request.POST['ridepk'])
        
    return render(request,'rideBrowseDriverCompleted.html',{'ride':ride})

@login_required
def rideBrowseSharerOpen(request):
    ride = Ride()
    if request.method == 'POST':
        ride = Ride.objects.get(pk = request.POST['ridepk'])
        
    return render(request,'rideBrowseSharerOpen.html',{'ride':ride})

@login_required
def rideBrowseSharerConfirmed(request):
    ride = Ride()
    if request.method == 'POST':
        ride = Ride.objects.get(pk = request.POST['ridepk'])
        
    return render(request,'rideBrowseSharerConfirmed.html',{'ride':ride})

@login_required
def rideBrowseSharerCompleted(request):
    ride = Ride()
    if request.method == 'POST':
        ride = Ride.objects.get(pk = request.POST['ridepk'])
        
    return render(request,'rideBrowseSharerCompleted.html',{'ride':ride})
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .form import *
from .models import profile
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def login_user(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:

                user_profile = profile.objects.get(account=user.id)
                if user_profile.role == 'systemAdmin':

                    login(request, user)

                    if next_url is not None:
                        return redirect(next_url)
                    else:
                        return redirect('profile')

                else:
                    messages.error(
                        request, "You don't have the required role.")
                    return redirect('login')
            except profile.DoesNotExist:
                messages.error(request, "Invalid credentials.")
                return redirect('login')
        else:
            messages.error(
                request, "Invalid credentials or Your Account is Suspended.")
            return redirect('login')
    else:
        return render(request, 'login.html', {})


@login_required(login_url='login')
def profile_view(request):
    path = request.path
    profiles = profile.objects.filter(role='systemAdmin')

    for prof in profiles:
        try:
            user = User.objects.get(id=prof.account_id)
            prof.accountStatus = user.is_active
        except User.DoesNotExist:
            prof.is_active = False

    title = 'System Administrator'

    return render(request, 'profile.html', {'profiles': profiles, 'title': title, 'path': path})


@login_required(login_url='login')
def medicalTech_profile(request):
    path = request.path
    profiles = profile.objects.filter(role='medicalTech')
    for prof in profiles:
        try:
            user = User.objects.get(id=prof.account_id)
            prof.accountStatus = user.is_active
        except User.DoesNotExist:
            prof.is_active = False

    title = 'Medical Technician'

    return render(request, 'profile.html', {'profiles': profiles, 'title': title, 'path': path})


@login_required(login_url='login')
def healthcareAdmin_profile(request):
    path = request.path
    profiles = profile.objects.filter(role='healthcareAdmin')
    for prof in profiles:
        try:
            user = User.objects.get(id=prof.account_id)
            prof.accountStatus = user.is_active
        except User.DoesNotExist:
            prof.is_active = False

    title = 'Healthcare Administrator'

    return render(request, 'profile.html', {'profiles': profiles, 'title': title, 'path': path})


@login_required(login_url='login')
def radiologyDoctor_profile(request):
    path = request.path
    profiles = profile.objects.filter(role='radiologyDoctor')
    for prof in profiles:
        try:
            user = User.objects.get(id=prof.account_id)
            prof.accountStatus = user.is_active
        except User.DoesNotExist:
            prof.is_active = False
    title = 'Radiology Doctor'

    return render(request, 'profile.html', {'profiles': profiles, 'title': title, 'path': path})


@login_required(login_url='login')
def systemAdmin_account(request):
    path = request.path
    accounts = User.objects.all()

    return render(request, 'account.html', {'accounts': accounts, 'path': path})


@csrf_protect
def createAccount_view(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('createProfile')
    else:
        form = CreateAccountForm()
        return render(request, 'forms.html', {'form': form})

    return render(request, 'forms.html', {'form': form})


def logout_user(request):
    request.session.clear()
    logout(request)
    return redirect(reverse('home'))


@csrf_protect
def create_profile(request):
    latest_user = User.objects.latest('date_joined')

    if request.method == 'POST':
        form = CreateProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()

            if profile.role == 'medicalTech':
                return redirect('medicalTech')
            elif profile.role == 'healthcareAdmin':
                return redirect('healthcareAdmin')
            elif profile.role == 'radiologyDoctor':
                return redirect('radiologyDoctor')
            else:
                return redirect('profile')
    else:
        initial_data = {
            'account': latest_user.username,
            'first_name': latest_user.first_name,
            'last_name': latest_user.last_name,
        }
        form = CreateProfileForm(initial=initial_data)

    return render(request, 'forms.html', {
        'form': form,
        'latest_user': latest_user,
    })


@csrf_protect
def update_profile(request, pk):
    current_profile = profile.objects.get(id=pk)

    if request.method == 'POST':
        form = update_profile_form(request.POST, instance=current_profile)
        if form.is_valid():
            form.save()
            if current_profile.role == 'medicalTech':
                return redirect('medicalTech')
            elif current_profile.role == 'healthcareAdmin':
                return redirect('healthcareAdmin')
            elif current_profile.role == 'radiologyDoctor':
                return redirect('radiologyDoctor')
            else:
                return redirect('profile')

    else:
        form = update_profile_form(instance=current_profile)

    return render(request, 'forms.html', {'form': form})


@csrf_protect
def update_account(request, accountID):

    current_account = User.objects.get(id=accountID)

    if request.method == 'POST':
        form = Update_Account_Form(request.POST, instance=current_account)
        if form.is_valid():
            form.save()
            return redirect('view_account')
    else:
        form = Update_Account_Form(instance=current_account)
        return render(request, 'forms.html', {'form': form})

    return render(request, 'forms.html', {'form': form})


@csrf_protect
def suspend_account(request, accountID):
    account = User.objects.get(id=accountID)
    account.is_active = False
    account.save()
    return redirect('view_account')


def unsuspend_account(request, accountID):
    account = User.objects.get(id=accountID)
    account.is_active = True
    account.save()
    return redirect('view_account')


def specific_account(request, accountID):
    acc = User.objects.filter(id=accountID)
    return render(request, 'account.html', {'accounts': acc, 'pk': accountID})

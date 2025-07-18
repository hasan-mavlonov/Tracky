from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import CustomUser
import time
import logging

logger = logging.getLogger(__name__)


@login_required(login_url='/login/')
def BaseView(request):
    start_time = time.time()
    logger.debug(
        f"User authenticated: {request.user.phone_number}, Role: {request.user.role}, Is authenticated: {request.user.is_authenticated}")
    end_time = time.time()
    logger.debug(f"Authentication processing took {end_time - start_time:.2f} seconds")
    return render(request, 'base.html', context={'message': 'Hello from the view!'})


def LandingView(request):
    return render(request, 'index.html')


def LoginView(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        logger.debug(f"Login attempt with phone_number: {phone_number}")
        user = authenticate(request, username=phone_number, password=password)
        if user is not None:
            logger.debug(f"Authentication successful for {phone_number}")
            login(request, user)
            next_url = request.POST.get('next', '/dashboard')
            return redirect(next_url)
        else:
            logger.debug(f"Authentication failed for {phone_number}")
            return render(request, 'registration/login.html', {
                'error': 'Invalid phone number or password.'
            })
    return render(request, 'registration/login.html')


@login_required(login_url='/login/')
def LogoutView(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def CreateUserView(request):
    if not request.user.can_create_users():
        messages.error(request, "You do not have permission to create users.")
        return redirect('base_view')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        role = request.POST.get('role')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        allowed_roles = request.user.allowed_roles_to_create()
        if role not in allowed_roles:
            messages.error(request, f"Invalid role selected. Allowed roles: {', '.join(allowed_roles)}.")
            return render(request, 'create_user.html')

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists.")
            return render(request, 'create_user.html')

        try:
            CustomUser.objects.create_user(
                phone_number=phone_number,
                password=password,
                role=role,
                first_name=first_name,
                last_name=last_name,
                is_staff=(role in ['tracky_admin', 'store_admin'])
            )
            messages.success(request, f"User {phone_number} created successfully.")
            return redirect('base_view')
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'create_user.html')

    return render(request, 'create_user.html', {
        'roles': request.user.allowed_roles_to_create()
    })


def ForgotPasswordView(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        messages.info(request, "Password reset feature coming soon!")
        return redirect('login')
    return render(request, 'registration/forgot_password.html')

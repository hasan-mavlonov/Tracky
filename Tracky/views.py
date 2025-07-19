import logging
import time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, ExpressionWrapper, F, DecimalField
from django.shortcuts import render, redirect

from products.models import Product
from shops.models import Shop
from users.models import CustomUser

logger = logging.getLogger(__name__)


@login_required(login_url='/login/')
def BaseView(request):
    start_time = time.time()
    logger.debug(
        f"User authenticated: {request.user.phone_number}, Role: {request.user.role}, Is authenticated: {request.user.is_authenticated}")

    total_sum = 0.00
    queryset = Product.objects.all()
    if request.user.role == 'superuser':
        queryset = queryset
    elif request.user.role == 'store_admin' and request.user.shop:
        queryset = queryset.filter(shop=request.user.shop)
    else:
        queryset = queryset.none()

    # Optionally filter for IN_STOCK if confirmed
    # queryset = queryset.filter(instances__status='IN_STOCK')

    total_sum = queryset.annotate(
        total_value=ExpressionWrapper(
            F('selling_price') * F('quantity'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    ).aggregate(Sum('total_value'))['total_value__sum'] or 0.00

    context = {
        'message': 'Welcome to the Dashboard!',
        'user_display_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.phone_number,
        'user_role': request.user.get_role_display(),
        'total_sum': total_sum,
    }
    end_time = time.time()
    logger.debug(f"BaseView processing took {end_time - start_time:.2f} seconds, Total sum: {total_sum}")
    return render(request, 'dashboard.html', context)


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
        shop_id = request.POST.get('shop')

        allowed_roles = request.user.allowed_roles_to_create()
        if role not in allowed_roles:
            messages.error(request, f"Invalid role selected. Allowed roles: {', '.join(allowed_roles)}.")
            return render(request, 'create_user.html')

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists.")
            return render(request, 'create_user.html')

        try:
            shop = None
            if shop_id:
                shop = Shop.objects.get(id=shop_id)
                if request.user.role == 'store_admin' and request.user.shop != shop:
                    messages.error(request, "You can only assign users to your own shop.")
                    return render(request, 'create_user.html')

            CustomUser.objects.create_user(
                phone_number=phone_number,
                password=password,
                role=role,
                first_name=first_name,
                last_name=last_name,
                shop=shop,
                is_staff=(role in ['tracky_admin', 'store_admin'])
            )
            messages.success(request, f"User {phone_number} created successfully.")
            return redirect('base_view')
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'create_user.html')
        except Shop.DoesNotExist:
            messages.error(request, "Selected shop does not exist.")
            return render(request, 'create_user.html')

    shops = Shop.objects.all() if request.user.role in ['superuser', 'tracky_admin'] else [request.user.shop]
    return render(request, 'create_user.html', {
        'roles': request.user.allowed_roles_to_create(),
        'shops': shops
    })


def ForgotPasswordView(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        messages.info(request, "Password reset feature coming soon!")
        return redirect('login')
    return render(request, 'registration/forgot_password.html')

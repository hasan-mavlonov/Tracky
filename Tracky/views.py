# Tracky/views.py
import logging
import time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, DecimalField
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import ProductInstance
from shops.models import Shop
from users.models import CustomUser

logger = logging.getLogger(__name__)


@login_required(login_url='/login/')
def BaseView(request):
    start_time = time.time()
    logger.debug(
        f"User authenticated: {request.user.phone_number}, Role: {request.user.role}, Is authenticated: {request.user.is_authenticated}")

    today = timezone.now().date()
    daily_sales = 0.00
    queryset = ProductInstance.objects.filter(status='SOLD', created_at__date=today)
    if request.user.role == 'superuser':
        queryset = queryset
    elif request.user.role in ['store_admin', 'manager', 'seller'] and request.user.shop:
        queryset = queryset.filter(product__shop=request.user.shop)
    else:
        queryset = queryset.none()

    daily_sales = queryset.annotate(
        sale_value=F('product__selling_price')
    ).aggregate(Sum('sale_value', output_field=DecimalField(max_digits=12, decimal_places=2)))[
                      'sale_value__sum'] or 0.00

    context = {
        'message': 'Welcome to the Dashboard!',
        'user_display_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.phone_number,
        'user_role': request.user.get_role_display(),
        'daily_sales': daily_sales,
    }
    end_time = time.time()
    logger.debug(f"BaseView processing took {end_time - start_time:.2f} seconds, Daily sales: {daily_sales}")
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


class APILoginView(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        logger.debug(f"API login request: {request.headers}, body={request.body}")
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        logger.debug(f"API login attempt: phone_number={phone_number}")
        if not phone_number or not password:
            return Response({"error": "Missing phone number or password"}, status=400)
        user = authenticate(username=phone_number, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            logger.info(f"API login successful: {phone_number}, token={token.key}")
            return Response({"token": token.key})
        logger.error(f"API login failed: {phone_number}")
        return Response({"error": "Invalid credentials"}, status=401)

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return JsonResponse({"error": "Authentication required"}, status=401)
        token_key = auth[len("Bearer "):]
        try:
            Token.objects.get(key=token_key)
            return JsonResponse({"status": "valid"}, status=200)
        except Token.DoesNotExist:
            return JsonResponse({"error": "Invalid token"}, status=401)

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import View

from .forms import CustomUserCreationForm

logger = logging.getLogger(__name__)


class CreateUserView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'create_user.html'

    def get(self, request):
        if not request.user.can_create_users():
            messages.error(request, "You do not have permission to create users.")
            return redirect('product-list')

        form = CustomUserCreationForm(user=request.user)
        context = {
            'form': form,
            'user_role': request.user.get_role_display(),
            'user_full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.phone_number,
            'can_create_users': request.user.can_create_users(),
        }
        logger.debug(f"Rendering create_user form for user: {request.user.phone_number}, role: {request.user.role}")
        return render(request, self.template_name, context)

    def post(self, request):
        if not request.user.can_create_users():
            messages.error(request, "You do not have permission to create users.")
            return redirect('product-list')

        form = CustomUserCreationForm(request.POST, user=request.user)
        logger.debug(f"POST data: {request.POST}, Form errors: {form.errors}")
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.phone_number} created successfully.")
            return redirect('product-list')
        else:
            messages.error(request, "Please correct the errors below.")
            logger.debug(f"Form validation failed for user: {request.user.phone_number}, errors: {form.errors}")

        context = {
            'form': form,
            'user_role': request.user.get_role_display(),
            'user_full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.phone_number,
            'can_create_users': request.user.can_create_users(),
        }
        return render(request, self.template_name, context)

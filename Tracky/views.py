from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def BaseView(request):
    return render(request, 'base.html', context={'message': 'Hello from the view!'})


def LandingView(request):
    return render(request, 'index.html')


def LoginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to home page or 'next' URL if provided
            next_url = request.POST.get('next', '/dashboard')
            return redirect(next_url)
        else:
            # Handle invalid credentials (e.g., show error message)
            return render(request, 'registration/login.html', {
                'error': 'Invalid username or password.'
            })
    return render(request, 'registration/login.html')

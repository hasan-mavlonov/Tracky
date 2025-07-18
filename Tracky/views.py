from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required(login_url='/login/')
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
            next_url = request.POST.get('next', '/dashboard')
            return redirect(next_url)
        else:
            return render(request, 'registration/login.html', {
                'error': 'Invalid username or password.'
            })
    return render(request, 'registration/login.html')

@login_required(login_url='/login/')
def LogoutView(request):
    logout(request)
    return render(request, 'registration/logout.html')
from django.shortcuts import render


def BaseView(request):
    return render(request, 'base.html', context={'message': 'Hello from the view!'})
def LandingView(request):
    return render(request, 'index.html')
def LoginView(request):
    return render(request, 'registration/login.html')
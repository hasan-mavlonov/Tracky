from django.shortcuts import render


def BaseView(request):
    return render(request, 'base.html', context={'message': 'Hello from the view!'})

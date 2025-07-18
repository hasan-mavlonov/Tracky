from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required(login_url='/login/')
def sell_products_view(request):
    return render(request, 'sales/sell.html')

@login_required(login_url='/login/')
def sell_scanned_products_view(request):
    return render(request, 'sales/sell_confirm.html')

@login_required(login_url='/login/')
def refund_product_view(request):
    return render(request, 'sales/refund.html')

@login_required(login_url='/login/')
def lookup_refund_rfid(request):
    return JsonResponse({'status': 'success'})

@login_required(login_url='/login/')
def refund_scanned_products(request):
    return JsonResponse({'status': 'success'})
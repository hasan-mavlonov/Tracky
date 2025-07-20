from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from products.models import Product  # Assuming a Product model exists


@login_required(login_url='/login/')
def sell_products_view(request):
    return render(request, 'sell_products.html')


@login_required(login_url='/login/')
def sell_scanned_products_view(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            rfids = data.get('rfids', [])

            if not rfids:
                return JsonResponse({'status': 'error', 'message': 'No products to sell'})

            # Fetch products by RFID
            sold_products = Product.objects.filter(rfid__in=rfids).values('rfid', 'name', 'price', 'barcode')

            if not sold_products:
                return JsonResponse({'status': 'error', 'message': 'No valid products found'})

            # Store sold products in session for confirm_sold_products
            request.session['sold_products'] = list(sold_products)
            request.session.modified = True

            # Perform sale logic (e.g., update product status, create sale record)
            # For now, assume sale is successful
            return JsonResponse({
                'status': 'success',
                'sold': list(sold_products)
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return redirect('confirm_sold_products')


@login_required(login_url='/login/')
def confirm_sold_products(request):
    try:
        # Retrieve sold products from session
        sold_products = request.session.get('sold_products', [])

        if not sold_products:
            return JsonResponse({
                'status': 'error',
                'message': 'No sale data found'
            })

        return JsonResponse({
            'status': 'success',
            'sold': sold_products
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error retrieving sale data: {str(e)}'
        })


@login_required(login_url='/login/')
def refund_product_view(request):
    return render(request, 'refund_products.html')


@login_required(login_url='/login/')
def lookup_refund_rfid(request):
    return JsonResponse({'status': 'success'})


@login_required(login_url='/login/')
def refund_scanned_products(request):
    return JsonResponse({'status': 'success'})
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Sale, SoldItem, Refund, RefundedItem
from products.models import ProductInstance, Product


def sell_products_view(request):
    return render(request, "sell_products.html")


@csrf_exempt
def sell_scanned_products_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            rfids = data.get("rfids", [])

            sale = Sale.objects.create()
            sold_items = []

            for rfid in rfids:
                instance = ProductInstance.objects.select_related("product").filter(RFID=rfid,
                                                                                    status="IN_STOCK").first()
                if instance:
                    instance.status = "SOLD"
                    instance.save()

                    product = instance.product
                    product.quantity = max(product.quantity - 1, 0)
                    product.save()

                    SoldItem.objects.create(sale=sale, product_instance=instance)
                    sold_items.append(rfid)

            return JsonResponse({"status": "success", "sold": sold_items})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"})


@csrf_exempt
def refund_product_view(request):
    if request.method == 'POST':
        rfid_code = request.POST.get('rfid')
        try:
            product_instance = ProductInstance.objects.get(RFID=rfid_code)  # Make sure casing is correct
            sold_item = SoldItem.objects.get(product_instance=product_instance)

            if RefundedItem.objects.filter(sold_item=sold_item).exists():
                messages.error(request, 'This product was already refunded.')
            else:
                refund = Refund.objects.create()
                RefundedItem.objects.create(refund=refund, sold_item=sold_item)

                # Also update product status and quantity if needed
                product_instance.status = "IN_STOCK"
                product_instance.save()

                product = product_instance.product
                product.quantity += 1
                product.save()

                messages.success(request, f"Product {product_instance} refunded successfully.")
        except ProductInstance.DoesNotExist:
            messages.error(request, 'No product with this RFID.')
        except SoldItem.DoesNotExist:
            messages.error(request, 'This product was not sold before.')

        return redirect('refund_scanned_products')  # Make sure this matches the name in urls.py

    return render(request, 'refund_products.html')


@csrf_exempt
def lookup_refund_rfid(request):
    if request.method == "POST":
        rfid_code = request.POST.get('rfid')
        try:
            product_instance = ProductInstance.objects.select_related("product").get(RFID=rfid_code, status="SOLD")

            return JsonResponse({
                'status': 'success',
                'product': {
                    'name': product_instance.product.name,
                    'price': product_instance.product.selling_price,
                    'barcode': product_instance.product.barcode
                }
            })

        except ProductInstance.DoesNotExist:
            return JsonResponse({'status': 'not_found'})
    return JsonResponse({'status': 'invalid'})


@csrf_exempt
def refund_scanned_products(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rfids = data.get('rfids', [])
            refunded_items = []

            for rfid in rfids:
                try:
                    product_instance = ProductInstance.objects.select_related("product").get(RFID=rfid, status="SOLD")
                    sold_item = SoldItem.objects.get(product_instance=product_instance)

                    if not RefundedItem.objects.filter(sold_item=sold_item).exists():
                        refund = Refund.objects.create()
                        RefundedItem.objects.create(refund=refund, sold_item=sold_item)

                        product_instance.status = "IN_STOCK"
                        product_instance.save()

                        product = product_instance.product
                        product.quantity += 1
                        product.save()

                        refunded_items.append(rfid)
                except (ProductInstance.DoesNotExist, SoldItem.DoesNotExist):
                    continue  # skip bad rfids silently

            return JsonResponse({'status': 'success', 'refunded': refunded_items})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

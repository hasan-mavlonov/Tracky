from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from products.models import ProductInstance, Product
from .models import Sale, SoldItem
import json


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

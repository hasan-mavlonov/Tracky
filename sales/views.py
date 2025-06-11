import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from products.models import ProductInstance
from .models import Sale


@csrf_exempt
def scan_rfid_view(request):
    if request.method == "POST":
        rfid = request.POST.get("rfid", "").strip()
        if not rfid:
            return JsonResponse({"status": "error", "message": "No RFID provided"})

        instance = ProductInstance.objects.select_related("product", "shop").filter(RFID=rfid).first()
        if instance:
            product = instance.product
            return JsonResponse({
                "status": "success",
                "product": {
                    "name": product.name,
                    "price": product.selling_price,
                    "barcode": product.barcode,
                    "shop": instance.shop.name,
                    "sold_at": instance.pk,  # or use timezone.now().strftime(...)
                    "rfid": rfid,
                }
            })
        else:
            return JsonResponse({"status": "not_found", "message": "RFID not found"})

    return JsonResponse({"status": "error", "message": "Invalid request"})


@csrf_exempt
def register_sale_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))  # 🔥 decode fix
            rfids = data.get("rfids", [])

            if not rfids or not isinstance(rfids, list):
                return JsonResponse({"status": "error", "message": "No valid RFID list provided"})

            results = []
            for rfid in rfids:
                instance = ProductInstance.objects.select_related("product", "shop").filter(RFID=rfid).first()
                if instance:
                    sale = Sale.objects.create(
                        product_instance=instance,
                        shop=instance.shop,
                        quantity=1,
                        selling_price=instance.product.selling_price
                    )
                    results.append({
                        "rfid": rfid,
                        "name": instance.product.name,
                        "barcode": instance.product.barcode,
                        "price": str(sale.selling_price),
                        "shop": instance.shop.name,
                        "sold_at": sale.sold_at.strftime('%Y-%m-%d %H:%M:%S')
                    })

            return JsonResponse({"status": "success", "sales": results})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"})

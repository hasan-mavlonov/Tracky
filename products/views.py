# products/views.py
from django.urls import reverse_lazy
from rest_framework import generics, status
from rest_framework.response import Response
from shops.models import Shop
from .forms import ProductForm
from .serializers import ProductSerializer
from .utils import generate_barcode
import json
from django.core.cache import cache
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.shortcuts import redirect
from .utils import generate_barcode_image
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST, require_GET
from .models import Product, ProductInstance
import base64
from io import BytesIO
from django.contrib import messages
from django.db.models import F
import time
import logging
logger = logging.getLogger(__name__)

class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        shops = Shop.objects.all()
        return render(request, 'create_product.html', {'shops': shops})

    def post(self, request, *args, **kwargs):
        barcode = request.data.get('barcode', None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not barcode:
            product_name = serializer.validated_data['name']
            barcode_image, barcode_code = generate_barcode(product_name)
            serializer.validated_data['barcode'] = barcode_code

        product = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'message': 'Product created successfully, barcode generated if not provided'
        }, status=status.HTTP_201_CREATED, headers=headers)


class ProductListAPIView(ListView):
    model = Product
    template_name = "products.html"
    context_object_name = "products"
    ordering = ["-created_at"]


class ProductDetailView(DetailView):
    model = Product
    template_name = "product.html"
    context_object_name = "product"


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "product_edit.html"
    success_url = "/products/all"


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "product_confirm_delete.html"
    success_url = reverse_lazy("product-list")


def generate_barcode_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = data.get('name')
            if not product_name:
                return JsonResponse({'error': 'Product name is required'}, status=400)
            barcode_image, barcode_code = generate_barcode(product_name)
            return JsonResponse({'barcode': barcode_code})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


LABEL_PRESETS = {
    "Default (44x18mm)": {"width": 44, "height": 18},
    "Small (58x30mm)": {"width": 58, "height": 30},
    "Medium (70x35mm)": {"width": 70, "height": 35},
    "Large (100x50mm)": {"width": 100, "height": 50},
}


def print_product_barcode_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        remaining_capacity = product.quantity - product.rfid_count
        if qty > remaining_capacity:
            messages.error(request, f"Only {remaining_capacity} unbound items available. Cannot print {qty} barcodes.")
            return render(request, 'choose_quantity.html', {'product': product, 'label_presets': LABEL_PRESETS})

        request.session.pop('pending_print_pk', None)
        request.session.pop('pending_print_qty', None)
        request.session.pop('bound_rfids', None)

        request.session['pending_print_pk'] = product.pk
        request.session['pending_print_qty'] = qty
        request.session['bound_rfids'] = []
        request.session.modified = True

        image = generate_barcode_image(product.barcode)
        buf = BytesIO()
        image.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        label_params = {
            'width': int(request.POST.get('width', 44)),
            'height': int(request.POST.get('height', 18)),
            'font_size_product_name': int(request.POST.get('font_name', 6)),
            'font_size_product_price': int(request.POST.get('font_price', 7)),
            'font_size_barcode': int(request.POST.get('font_barcode', 6)),
            'barcode_width': int(request.POST.get('barcode_width', 90)),
            'barcode_height': int(request.POST.get('barcode_height', 8)),
            'product_name_max_width': request.POST.get('name_max_width'),
        }

        return render(request, 'print_barcode.html', {
            'product': product,
            'quantity_range': range(qty),
            'img_b64': img_b64,
            **label_params,
        })

    return render(request, 'choose_quantity.html', {
        'product': product,
        'label_presets': LABEL_PRESETS
    })


@require_POST
def bind_rfid_view(request, pk):
    pending_pk = request.session.get('pending_print_pk')
    qty = request.session.get('pending_print_qty', 0)
    bound_rfids = request.session.get('bound_rfids', [])
    rfid_code = request.POST.get('rfid', '').strip()

    if not pending_pk or pending_pk != pk:
        return JsonResponse({'status': 'error', 'message': 'No matching print job queued.'}, status=400)
    if not rfid_code:
        return JsonResponse({'status': 'error', 'message': 'No RFID received.'}, status=400)
    if rfid_code in bound_rfids:
        return JsonResponse({'status': 'error', 'message': 'RFID already bound in session.'}, status=400)
    if ProductInstance.objects.filter(RFID=rfid_code).exists():
        return JsonResponse({'status': 'error', 'message': 'RFID already exists in database.'}, status=400)

    try:
        product = get_object_or_404(Product, pk=pk)
        if not product.has_available_rfid_slots():
            return JsonResponse({'status': 'error', 'message': 'All RFIDs already assigned to this product. Cannot exceed quantity.'}, status=400)

        ProductInstance.objects.create(product=product, RFID=rfid_code)
        product.rfid_count = F('rfid_count') + 1
        product.save(update_fields=['rfid_count'])
        bound_rfids.append(rfid_code)
        request.session['bound_rfids'] = bound_rfids
        request.session.modified = True

        remaining = qty - len(bound_rfids)
        if remaining <= 0:
            request.session.pop('pending_print_pk', None)
            request.session.pop('pending_print_qty', None)
            request.session.pop('bound_rfids', None)
            return JsonResponse({'status': 'done', 'message': 'All RFIDs bound.', 'remaining': 0})

        return JsonResponse({'status': 'success', 'message': f'RFID {rfid_code} bound.', 'remaining': remaining})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error processing RFID: {str(e)}'}, status=500)


def bind_rfid_page_view(request, pk):
    pending_pk = request.session.get('pending_print_pk')
    qty = request.session.get('pending_print_qty', 0)
    bound_rfids = request.session.get('bound_rfids', [])

    if not pending_pk or pending_pk != pk:
        return HttpResponse("No RFID binding session found.", status=400)

    product = get_object_or_404(Product, pk=pk)
    remaining = qty - len(bound_rfids)
    return render(request, 'bind_rfids.html', {'product': product, 'remaining': remaining})


def choose_quantity_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        return redirect(f'/print-barcode/{pk}/?qty={qty}')
    return render(request, 'choose_quantity.html', {'product': product})


def cancel_print_session(request):
    if request.method == 'POST':
        request.session.pop('pending_print_pk', None)
        request.session.pop('pending_print_qty', None)
        request.session.pop('bound_rfids', None)
        return JsonResponse({'status': 'cancelled'})
    return JsonResponse({'status': 'error'}, status=405)


def check_rfid_view(request):
    return render(request, "check_rfid.html")


@require_GET
def current_products(request):
    try:
        tag_dict = cache.get("current_rfids_dict", {}) or {}
        raw_rfids = list(tag_dict.keys())
        logger.debug(f"Current RFIDs from cache: {raw_rfids}")

        # Normalize RFIDs for both formats
        normalized_rfids = []
        for rfid in raw_rfids:
            # Handle agent format (01 prefix)
            if rfid.startswith('01') and len(rfid) == 24:
                normalized_rfids.append(rfid[2:] + 'C8')  # Convert to server format
            else:
                normalized_rfids.append(rfid)

        qs = (
            ProductInstance.objects
            .select_related("product")
            .filter(RFID__in=normalized_rfids)
            .exclude(status__in=['SOLD', 'LOST', 'DAMAGED'])
        )

        products = []
        for inst in qs:
            products.append({
                "rfid": inst.RFID,  # Return exactly what's in DB
                "name": inst.product.name,
                "price": float(inst.product.selling_price),
                "barcode": inst.product.barcode,
                "status": inst.status,
            })

        return JsonResponse({
            "products": products,
            "raw_rfids": raw_rfids  # The original normalized ones from cache
        })
    except Exception as e:
        logger.error(f"Error in current_products: {e}")
        return JsonResponse({"products": [], "raw_rfids": []})


@csrf_protect
@require_POST
def lookup_rfid_view(request):
    """
    Manual lookup form (Enter RFID + Enter).
    Expects form-encoded POST: rfid=TAGID
    """
    try:
        rfid = request.POST.get("rfid", "").strip().upper()
        if not rfid:
            return JsonResponse({"status": "error", "message": "No RFID provided"})

        inst = ProductInstance.objects.select_related("product").filter(RFID=rfid).first()
        if inst:
            prod = inst.product
            return JsonResponse({
                "status": "success",
                "product": {
                    "name": prod.name,
                    "price": float(prod.selling_price),
                    "barcode": prod.barcode,
                    "status": inst.status,
                }
            })

        return JsonResponse({"status": "not_found", "message": "RFID not found"})
    except Exception as e:
        logger.error(f"Error in lookup_rfid_view: {e}")
        return JsonResponse({"status": "error", "message": "Server error"}, status=500)

@require_POST
def cancel_print_session_view(request):
    request.session.pop('pending_print_pk', None)
    request.session.pop('pending_print_qty', None)
    request.session.pop('bound_rfids', None)
    return JsonResponse({'status': 'success'})



@csrf_exempt
@require_POST
def store_rfids_view(request):
    """
    POST {"rfids": ["TAG1", "TAG2", ...]}
    → updates cache['current_rfids_dict'] = { tag: timestamp }
    """
    try:
        data = json.loads(request.body)
        rfids = data.get("rfids", [])
        if not isinstance(rfids, list):
            return JsonResponse({"error": "Invalid format"}, status=400)

        now = time.time()
        existing = cache.get("current_rfids_dict", {}) or {}
        for rfid in rfids:
            existing[rfid.strip().upper()] = now
        # keep them alive for 2s unless refreshed
        cache.set("current_rfids_dict", existing, timeout=2)

        logger.debug(f"Stored RFIDs: {list(existing.keys())}")
        return JsonResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Error in store_rfids_view: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@require_GET
def current_sold_products(request):
    """
    Returns currently scanned products that are marked as SOLD in the DB.
    Used in refund flow to identify refundable products within RFID range.
    """
    try:
        tag_dict = cache.get('current_rfids_dict', {}) or {}
        raw_rfids = list(tag_dict.keys())

        logger.debug(f"Current SOLD RFIDs in range: {raw_rfids}")

        queryset = (
            ProductInstance.objects
            .select_related("product")
            .filter(RFID__in=raw_rfids, status="SOLD")
        )

        products = []
        for inst in queryset:
            products.append({
                "rfid": inst.RFID.strip().upper(),
                "name": inst.product.name,
                "price": float(inst.product.selling_price),
                "barcode": inst.product.barcode,
                "status": inst.status,
            })

        return JsonResponse({
            "products": products,
            "raw_rfids": raw_rfids
        })
    except Exception as e:
        logger.error(f"Error in current_sold_products: {e}")
        return JsonResponse({"products": [], "raw_rfids": []})
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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Product, ProductInstance
import base64
from io import BytesIO
from django.contrib import messages
from django.db.models import F
import time
import logging
class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        # Fetch all shops from the database and pass them to the template
        shops = Shop.objects.all()
        return render(request, 'create_product.html', {'shops': shops})

    def post(self, request, *args, **kwargs):
        # Handle form submission and product creation
        barcode = request.data.get('barcode', None)
        serializer = self.get_serializer(data=request.data)

        # Check if the provided data is valid
        serializer.is_valid(raise_exception=True)

        # If no barcode is provided, generate one
        if not barcode:
            product_name = serializer.validated_data['name']
            barcode_image, barcode_code = generate_barcode(product_name)
            serializer.validated_data['barcode'] = barcode_code  # Set the generated barcode

        # Save the product, now with the barcode (either provided or generated)
        product = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'status': 'success',
                'data': serializer.data,
                'message': 'Product created successfully, barcode generated if not provided'
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class ProductListAPIView(ListView):
    model = Product
    template_name = "products.html"  # your template
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
    success_url = "/products/all"  # or use reverse_lazy('product-list')


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "product_confirm_delete.html"
    success_url = reverse_lazy("product-list")  # or wherever you want to redirect



def generate_barcode_view(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)

            product_name = data.get('name')

            if not product_name:
                return JsonResponse({'error': 'Product name is required'}, status=400)

            barcode_image, barcode_code = generate_barcode(product_name)

            # Return the generated barcode as a response
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
            messages.error(
                request,
                f"Only {remaining_capacity} unbound items available. Cannot print {qty} barcodes."
            )
            return render(request, 'choose_quantity.html', {
                'product': product,
                'label_presets': LABEL_PRESETS
            })

        # Clear previous session data
        request.session.pop('pending_print_pk', None)
        request.session.pop('pending_print_qty', None)
        request.session.pop('bound_rfids', None)

        request.session['pending_print_pk'] = product.pk
        request.session['pending_print_qty'] = qty
        request.session['bound_rfids'] = []
        request.session.modified = True

        # Generate barcode image
        image = generate_barcode_image(product.barcode)
        buf = BytesIO()
        image.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        # Get label customization from POST
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
  # REMOVE in production
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

        # ✅ Check RFID slot availability
        if not product.has_available_rfid_slots():
            return JsonResponse({
                'status': 'error',
                'message': 'All RFIDs already assigned to this product. Cannot exceed quantity.'
            }, status=400)

        # ✅ Create the ProductInstance
        ProductInstance.objects.create(product=product, RFID=rfid_code)

        # ✅ Increment the rfid_count
        product.rfid_count = F('rfid_count') + 1
        product.save(update_fields=['rfid_count'])

        # ✅ Update session
        bound_rfids.append(rfid_code)
        request.session['bound_rfids'] = bound_rfids
        request.session.modified = True

        remaining = qty - len(bound_rfids)
        if remaining <= 0:
            # ✅ Clear session when done
            request.session.pop('pending_print_pk', None)
            request.session.pop('pending_print_qty', None)
            request.session.pop('bound_rfids', None)

            return JsonResponse({
                'status': 'done',
                'message': 'All RFIDs bound.',
                'remaining': 0
            })

        return JsonResponse({
            'status': 'success',
            'message': f'RFID {rfid_code} bound.',
            'remaining': remaining
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing RFID: {str(e)}'
        }, status=500)


def bind_rfid_page_view(request, pk):
    pending_pk = request.session.get('pending_print_pk')
    qty = request.session.get('pending_print_qty', 0)
    bound_rfids = request.session.get('bound_rfids', [])

    if not pending_pk or pending_pk != pk:
        return HttpResponse("No RFID binding session found.", status=400)

    product = get_object_or_404(Product, pk=pk)
    remaining = qty - len(bound_rfids)

    return render(request, 'bind_rfids.html', {
        'product': product,
        'remaining': remaining
    })


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


logger = logging.getLogger(__name__)

def check_rfid_view(request):
    return render(request, "check_rfid.html")

def current_products(request):
    try:
        now = time.time()
        tag_dict = cache.get('current_rfids_dict', {})

        # Only use tags seen in the last 1 second
        recent_tags = [tag for tag, ts in tag_dict.items() if now - ts <= 1.0]
        logger.debug(f"Current RFIDs from reader: {recent_tags}")

        qs = (
            ProductInstance.objects
            .select_related("product")
            .filter(RFID__in=recent_tags)
            .exclude(status__in=['SOLD', 'LOST', 'DAMAGED'])
        )

        products = []
        for inst in qs:
            r = inst.RFID.strip().upper()
            products.append({
                "rfid": r,
                "name": inst.product.name,
                "price": float(inst.product.selling_price),
                "barcode": inst.product.barcode,
                "status": inst.status,
            })

        return JsonResponse({
            "products": products,
            "raw_rfids": recent_tags
        })

    except Exception as e:
        logger.error(f"Error in current_products: {e}")
        return JsonResponse({"products": [], "raw_rfids": []})



def lookup_rfid_view(request):
    if request.method == "POST":
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
            return JsonResponse({"status": "error", "message": "Server error"})
    return JsonResponse({"status": "error", "message": "Invalid request method"})

@require_POST
def cancel_print_session_view(request):
    request.session.pop('pending_print_pk', None)
    request.session.pop('pending_print_qty', None)
    request.session.pop('bound_rfids', None)
    return JsonResponse({'status': 'success'})


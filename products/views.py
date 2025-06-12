# products/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from shops.models import Shop
from .serializers import ProductSerializer
from .utils import generate_barcode
import json

from django.shortcuts import redirect
from .utils import generate_barcode_image
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Product, ProductInstance
import base64
from io import BytesIO


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


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'status': 'success', 'message': 'Product deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


@csrf_exempt
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


def print_product_barcode_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))

        # Clear any previous session data
        request.session.pop('pending_print_pk', None)
        request.session.pop('pending_print_qty', None)
        request.session.pop('bound_rfids', None)

        # Save info for RFID binding
        request.session['pending_print_pk'] = product.pk
        request.session['pending_print_qty'] = qty
        request.session['bound_rfids'] = []
        request.session.modified = True  # Ensure session is saved

        # Generate barcode image once
        image = generate_barcode_image(product.barcode)
        buf = BytesIO()
        image.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        return render(request, 'print_barcode.html', {
            'product': product,
            'quantity_range': range(qty),
            'img_b64': img_b64,
        })

    return render(request, 'choose_quantity.html', {'product': product})


@require_POST
@csrf_exempt  # Temporarily exempt for testing, remove in production
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
        return JsonResponse({'status': 'error', 'message': 'RFID already bound.'}, status=400)

    try:
        product = get_object_or_404(Product, pk=pk)
        ProductInstance.objects.create(product=product, RFID=rfid_code)

        bound_rfids.append(rfid_code)
        request.session['bound_rfids'] = bound_rfids
        request.session.modified = True  # Ensure session is saved

        remaining = qty - len(bound_rfids)
        if remaining <= 0:
            # Clear session when done
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


@csrf_exempt
def cancel_print_session(request):
    if request.method == 'POST':
        request.session.pop('pending_print_pk', None)
        request.session.pop('pending_print_qty', None)
        request.session.pop('bound_rfids', None)
        return JsonResponse({'status': 'cancelled'})
    return JsonResponse({'status': 'error'}, status=405)


def check_rfid_view(request):
    return render(request, "check_rfid.html")


@csrf_exempt
def lookup_rfid_view(request):
    if request.method == "POST":
        rfid = request.POST.get("rfid", "").strip()  # ✅ STRIP INPUT

        if not rfid:
            return JsonResponse({"status": "error", "message": "No RFID provided"})

        instance = ProductInstance.objects.select_related("product").filter(RFID=rfid).first()

        if instance:
            if instance.status != "IN_STOCK":
                return JsonResponse({
                    "status": "error",
                    "message": f"Item unavailable: {instance.status.replace('_', ' ').title()}"
                })

            product = instance.product
            return JsonResponse({
                "status": "success",
                "product": {
                    "name": product.name,
                    "price": product.selling_price,
                    "barcode": product.barcode,
                }
            })

        return JsonResponse({"status": "not_found", "message": "RFID not found"})

    return JsonResponse({"status": "error", "message": "Invalid request method"})


@require_POST
def cancel_print_session_view(request):
    request.session.pop('pending_print_pk', None)
    request.session.pop('pending_print_qty', None)
    request.session.pop('bound_rfids', None)
    return JsonResponse({'status': 'success'})

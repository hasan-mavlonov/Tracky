# products/views.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.response import Response
from shops.models import Shop
from .serializers import ProductSerializer
from django.http import JsonResponse
from .utils import generate_barcode
import json
import base64
from io import BytesIO
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductInstance
from .utils import generate_barcode_image


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

        # Save info for RFID binding
        request.session['pending_print_pk'] = product.pk
        request.session['pending_print_qty'] = qty
        request.session['bound_rfids'] = []

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



@csrf_exempt
def bind_rfid_view(request, pk):
    if request.method == 'POST':
        rfid_code = request.POST.get('rfid', '').strip()
        pending_pk = request.session.get('pending_print_pk')
        qty = request.session.get('pending_print_qty', 0)
        bound_rfids = request.session.get('bound_rfids', [])

        if not pending_pk or pending_pk != pk:
            return JsonResponse({'status': 'error', 'message': 'No matching print job queued.'}, status=400)

        if not rfid_code:
            return JsonResponse({'status': 'error', 'message': 'No RFID received.'}, status=400)

        if rfid_code in bound_rfids:
            return JsonResponse({'status': 'error', 'message': 'RFID already bound.'}, status=400)

        product = get_object_or_404(Product, pk=pk)
        ProductInstance.objects.create(product=product, RFID=rfid_code)

        bound_rfids.append(rfid_code)
        request.session['bound_rfids'] = bound_rfids

        if len(bound_rfids) >= qty:
            del request.session['pending_print_pk']
            del request.session['pending_print_qty']
            del request.session['bound_rfids']
            return JsonResponse({'status': 'done', 'message': 'All RFIDs bound.'})

        return JsonResponse({'status': 'success', 'message': f'RFID {rfid_code} bound. {qty - len(bound_rfids)} left.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)


def choose_quantity_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        return redirect(f'/print-barcode/{pk}/?qty={qty}')
    return render(request, 'choose_quantity.html', {'product': product})

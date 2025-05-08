# products/views.py
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from django.http import JsonResponse
from .utils import generate_barcode
import json


class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        # This handles rendering the HTML template when the user accesses the page
        return render(request, 'create_product.html')

    def post(self, request, *args, **kwargs):
        # This handles the API request to create the product when the form is submitted
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

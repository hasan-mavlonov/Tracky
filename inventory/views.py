# inventory/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import ProductInstance, ShopInventory
from .serializers import ProductInstanceSerializer, ShopInventorySerializer
from products.models import Product
from shops.models import Shop


# Create a ProductInstance (RFID for a product in a specific shop)
class ProductInstanceCreateAPIView(generics.CreateAPIView):
    queryset = ProductInstance.objects.all()
    serializer_class = ProductInstanceSerializer

    def create(self, request, *args, **kwargs):
        product_data = request.data.get('product')
        shop_data = request.data.get('shop')

        # Check if the product and shop exist
        try:
            product = Product.objects.get(id=product_data)
            shop = Shop.objects.get(id=shop_data)
        except Product.DoesNotExist or Shop.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Product or Shop not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create ProductInstance
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Update the ShopInventory stock count
        shop_inventory, created = ShopInventory.objects.get_or_create(
            shop=shop,
            product=product
        )
        shop_inventory.stock_quantity += 1  # Increment stock for new instance
        shop_inventory.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            {'status': 'success', 'data': serializer.data, 'message': 'Product Instance created successfully'},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


# View for listing product instances
class ProductInstanceListAPIView(generics.ListAPIView):
    queryset = ProductInstance.objects.all()
    serializer_class = ProductInstanceSerializer


# View for product instance details (optional)
class ProductInstanceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductInstance.objects.all()
    serializer_class = ProductInstanceSerializer
    lookup_field = 'id'

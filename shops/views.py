from rest_framework import generics, status
from rest_framework.response import Response
from .models import Shop
from .serializers import ShopSerializer


class ShopCreateAPIView(generics.CreateAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'status': 'success',
                'data': serializer.data,
                'message': 'Shop created successfully'
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class ShopListAPIView(generics.ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class ShopDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    lookup_field = 'id'  # Make sure your URL uses <int:id>

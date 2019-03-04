from rest_framework import generics
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Category
from .serializers import CategorySerializer
from rest_framework.response import Response
from rest_framework import status
from authors.apps.articles.renderers import CategoryJSONRenderer


class CreateListCategory(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
    renderer_classes = (CategoryJSONRenderer,)
    queryset = Category.objects.all()

    def create(self, request, *args, **kwargs):
        category = request.data.get("category", {})
        serializer = self.get_serializer(data=category)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class RetrieveUpdateDestroyCategory(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    queryset = Category.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "category deleted"},
                        status=status.HTTP_204_NO_CONTENT)

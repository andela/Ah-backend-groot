from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Category, Article
from .serializers import CategorySerializer, ArticleSerializer
from authors.apps.articles.renderers import CategoryJSONRenderer
from .renderers import ArticleJSONRenderer


class CreateListCategory(ListCreateAPIView):
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


class RetrieveUpdateDestroyCategory(RetrieveUpdateDestroyAPIView):
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


class CreateArticle(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    def create(self, request):
        article = request.data.get('article', {})
        serializer = self.get_serializer(data=article)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleRetrieveUpdate(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_class = (ArticleJSONRenderer,)
    queryset = Article.objects.select_related('author', 'category')
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), slug=self.kwargs.get('slug'))

    def update(self, request, *args, **kwargs):
        self.serializer_instance = self.get_object()
        serializer_data = request.data.get('article', {})

        serializer = self.serializer_class(
            self.serializer_instance, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

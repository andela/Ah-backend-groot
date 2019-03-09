from django.urls import path

from .views import (RetrieveUpdateDestroyCategory,
                    CreateListCategory,
                    CreateArticle,
                    ArticleRetrieveUpdate)

urlpatterns = [
    path('categories/', CreateListCategory.as_view(), name='create-category'),
    path('categories/<str:slug>', RetrieveUpdateDestroyCategory.as_view(),
         name='update-delete'),
    path('articles/', CreateArticle.as_view(), name='create-articles'),
    path('article/<str:slug>/', ArticleRetrieveUpdate.as_view(),
         name='update-articles')
]

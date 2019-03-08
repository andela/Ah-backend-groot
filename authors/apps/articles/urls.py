from django.urls import path

from .views import RetrieveUpdateDestroyCategory, CreateListCategory

urlpatterns = [
    path('categories/', CreateListCategory.as_view(), name="create-articles"),
    path('categories/<str:slug>', RetrieveUpdateDestroyCategory.as_view(),
         name="update-delete")
]

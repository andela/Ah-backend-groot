"""authors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('home/', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('home/', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import path, include
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls',))
"""
from django.urls import include, path
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view
from rest_framework.documentation import include_docs_urls
from django.views.generic.base import RedirectView

coreapi_docs = include_docs_urls(title='Authors Haven')
schema_view = get_swagger_view(title='Authors Haven')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authors.apps.authentication.urls', )),
    path('swagger/', schema_view),
    path('docs/', coreapi_docs),
    path('', RedirectView.as_view(url='docs/', permanent=False), name='index')
]

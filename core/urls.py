from django.urls import path

from core.views import *

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('detail/<slug:slug>', ProductDetailView.as_view(), name='detail'),
    path('products/', ProductListView.as_view(), name='list'),
    path('products/<str:category>/', ProductListView.as_view(), name='list'),
]

from django.urls import path
from core.views import *

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('detail/<int:pk>', ProductDetailView.as_view(), name='detail'),
    path('list/', ProductListView.as_view(), name='list'),
    path('list/<str:category>/', ProductListView.as_view(), name='list'),
]

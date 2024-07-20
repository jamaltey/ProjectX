from django.urls import path
from core.views import *

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('detail/<int:pk>', detail, name='detail'),
    path('delete-comment/<int:pk>', delete_comment, name='delete-comment'),
    path('list/', list, name='list'),
    path('list/sales/', lambda r: list(r, sales=True), name='sales'),
]

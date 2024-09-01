from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'api'

router = DefaultRouter()
router.register(r'comment', CommentViewSet, basename='comment')

urlpatterns = router.urls

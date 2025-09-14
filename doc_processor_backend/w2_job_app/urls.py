from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import W2JobViewSet

router = DefaultRouter()
router.register(r'jobs', W2JobViewSet, basename='w2job')

urlpatterns = [
    path('', include(router.urls)),
]

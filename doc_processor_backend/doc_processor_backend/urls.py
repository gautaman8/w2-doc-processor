"""
URL configuration for doc_processor_backend project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('w2_job_app.urls')),
]

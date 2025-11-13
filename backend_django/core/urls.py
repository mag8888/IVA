"""
URLs for core app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('structure/', views.structure_view, name='structure'),
    path('queue/', views.queue_view, name='queue'),
]


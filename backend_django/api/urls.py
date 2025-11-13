"""
API URLs.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Статус API
    path('status/', views.api_status, name='api-status'),
    
    # Регистрация
    path('register/', views.register, name='api-register'),
    
    # Очередь регистраций
    path('queue/', views.queue, name='api-queue'),
    path('queue/public/', views.queue_public, name='api-queue-public'),
    
    # Завершение регистрации
    path('complete/', views.complete, name='api-complete'),
    
    # Структура MLM
    path('structure/', views.structure, name='api-structure'),
    path('structure/tree/', views.structure_tree, name='api-structure-tree'),
    
    # Бонусы (из базы данных)
    path('bonuses/', views.bonuses, name='api-bonuses'),
    
    # Тарифы
    path('tariffs/', views.tariffs, name='api-tariffs'),
    
    # Статистика (из базы данных)
    path('stats/', views.stats, name='api-stats'),
]


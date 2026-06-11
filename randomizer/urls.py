from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test-ml/', views.test_ml, name='test_ml'),
    path('room/<str:room_code>/', views.room, name='room'),
]

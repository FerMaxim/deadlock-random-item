from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<str:room_code>/', views.room, name='room'),
    path('api/generate_build/', views.api_generate_build, name='api_generate_build'),
]

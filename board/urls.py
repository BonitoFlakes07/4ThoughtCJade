from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<slug:slug>/', views.board_detail, name='board_detail'),
    path('<slug:slug>/thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
]
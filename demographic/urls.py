from django.urls import path
from . import views

app_name = 'demographic'

urlpatterns = [
    path('', views.home, name='home'),
    path('<slug:slug>/', views.single, name='single'),
]

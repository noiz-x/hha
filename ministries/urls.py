from django.urls import path
from . import views

app_name = 'ministries'

urlpatterns = [
    path('', views.home, name='home'),
    path('confirm/<uuid:unique_uuid>/', views.confirm, name='confirm'),
]

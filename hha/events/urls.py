from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.home, name='home'),
    path('all/', views.all_events, name='all_events'),
    path('confirm/<uuid:unique_uuid>/', views.confirm, name='confirm'),
    path('user-details/<str:token>/', views.user_details, name='user_details'),
    path('<slug:slug>/<str:date>/', views.single, name='single'),
]

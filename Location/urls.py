from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.location_login, name='location_login'),
    path('dashboard/', views.location_dashboard, name='location_dashboard'),
    path('sales/', views.location_sales, name='location_sales'),
    path('reports/', views.location_reports, name='location_reports'),
    path('feedback/', views.location_feedback, name='location_feedback'),
    path('settings/', views.location_settings, name='location_settings'),
    path('add_user/', views.add_location_user, name='add_location_user'),
    path('add_pos/', views.add_location_pos, name='add_location_pos'),
    path('assign_pos/', views.assign_location_pos, name='assign_location_pos'),
    path('about/', views.location_about, name='location_about'),
]

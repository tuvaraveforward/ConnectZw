from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.dealer_login, name='dealer_login'),
    path('dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('locations/', views.dealer_locations, name='dealer_locations'),
    path('sales/', views.dealer_sales, name='dealer_sales'),
    path('reports/', views.dealer_reports, name='dealer_reports'),
    path('settings/', views.dealer_settings, name='dealer_settings'),
    path('product/<int:product_id>/edit/', views.dealer_product_edit, name='dealer_product_edit'),
    path('product/<int:product_id>/delete/', views.dealer_product_delete, name='dealer_product_delete'),
    path('reset-password/', views.dealer_reset_password, name='dealer_reset_password'),
]

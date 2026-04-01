from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # path('signup/', views.admin_signup, name='admin_signup'), # Signup removed as per request
    path('locations/', views.locations, name='locations'),
    path('locations/register/', views.register_location, name='register_location'),
    path('locations/edit/<int:location_id>/', views.edit_location, name='edit_location'),
    path('locations/<int:location_id>/add_user/', views.add_user, name='add_user'),
    path('locations/<int:location_id>/add_pos/', views.add_pos, name='add_pos'),
    path('locations/delete/<int:location_id>/', views.delete_location, name='delete_location'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('accounts/', views.accounts, name='accounts'),
    path('admin/<int:admin_id>/edit/', views.edit_admin, name='edit_admin'),
    path('admin/<int:admin_id>/delete/', views.delete_admin, name='delete_admin'),
    path('client/<int:client_id>/edit/', views.edit_client, name='edit_client'),
    path('client/<int:client_id>/delete/', views.delete_client, name='delete_client'),
    path('sales/', views.sales, name='sales'),
    path('settings/', views.settings, name='settings'),
    path('reports/', views.reports, name='reports'),
    path('reset-password/', views.admin_reset_password, name='admin_reset_password'),
    path('feedbacks/', views.admin_feedbacks, name='admin_feedbacks'),
]

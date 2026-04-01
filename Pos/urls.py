from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.pos_login, name='pos_login'),
    path('dashboard/', views.pos_dashboard, name='pos_dashboard'),
    path('logout/', views.pos_logout, name='pos_logout'),
    path('redeem_coupon/', views.redeem_coupon, name='redeem_coupon'),
    path('check_validity/', views.pos_check_validity, name='pos_check_validity'),
    path('run_report/', views.pos_run_report, name='pos_run_report'),
    path('report_coupon/', views.pos_report_coupon, name='pos_report_coupon'),
    path('sales/', views.pos_sales, name='pos_sales'),
    path('settings/', views.pos_settings, name='pos_settings'),
]

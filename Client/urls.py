from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.client_login, name='client_login'),
    path('signup/', views.client_signup, name='client_signup'),
    path('dashboard/', views.client_dashboard, name='client_dashboard'),
    path('client_account/', views.client_account, name='client_account'),
    path('purchases/', views.client_purchases, name='client_purchases'),
    path('topup/', views.client_topup, name='client_topup'),
    path('history/', views.client_history, name='client_history'),
    path('settings/', views.client_settings, name='client_settings'),
    path('get-basket/', views.get_basket, name='get_basket'),
    path('add-to-basket/<int:product_id>/', views.add_to_basket, name='add_to_basket'),
    path('update-basket-item/<int:item_id>/', views.update_basket_item, name='update_basket_item'),
    path('remove-basket-item/<int:item_id>/', views.remove_basket_item, name='remove_basket_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('reset-password/', views.client_reset_password, name='client_reset_password'),
    path('service-request/<int:product_id>/', views.service_request, name='service_request'),
    path('service-confirm/<uuid:token>/', views.service_confirm, name='service_confirm'),
    path('service-decline/<uuid:token>/', views.service_decline, name='service_decline'),
    path('share-coupon-email/', views.share_coupon_via_email, name='share_coupon_email'),
    path('share-coupon/', views.share_coupon, name='share_coupon'),
    path('feedback/', views.client_feedback, name='client_feedback'),
    path('chat/', views.client_chat, name='client_chat'),
    path('category/<str:category>/', views.client_products, name='client_products'),
    path('cart/', views.client_cart, name='client_cart'),
]

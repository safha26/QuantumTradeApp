from django.urls import path
from . import views
from .views import dashboard

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('place_order/', views.place_order, name='place_order'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('api/order_book/', views.order_book_api, name='api_order_book'),
    path('api/trade_history/', views.trade_history_api, name='api_trade_history'),
    path('your_dashboard/', views.your_dashboard, name='your_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
]
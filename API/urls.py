from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name=('register')),
    path('token', views.TokenView.as_view()),
    path('', views.productList.as_view()),
    path('user/', views.userList.as_view()),
    path('cur/', views.CurView.as_view()),
    path('add/<str:pk>/', views.add),
    path('cart/', views.CartView.as_view()),
    path('remove/<str:pk>/', views.remove),
    path('save/<str:pk>/', views.favourite),
    path('favourite/', views.SaveView.as_view()),
    path('new', views.NewList.as_view()),

    #mpesa api urls
    path('access/token', views.getAccessToken, name='get_mpesa_access_token'),
    path('mpesa/lipa', views.lipa_na_mpesa_online, name='lipa_na_mpesa'),
    # register, confirmation, validation and callback urls
    path('api/c2b/register', views.register_urls, name="register_mpesa_validation"),
    path('api/c2b/confirmation', views.confirmation, name="confirmation"),
    path('api/c2b/validation', views.validation, name="validation"),
    path('api/c2b/callback', views.call_back, name="call_back"),
]
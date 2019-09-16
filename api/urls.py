from django.urls import path

from rest_framework_jwt.views import obtain_jwt_token

from . import views


app_name = 'api'

urlpatterns = [
    path('register', views.register, name="register"),
    path('auth', obtain_jwt_token, name='auth'),
    path('balance', views.BalanceUserView.as_view(), name='balance'),
    path('deposit', views.DepositView.as_view(), name='deposit'),
    path('withdraw', views.WithdrawView.as_view(), name='withdraw'),
]
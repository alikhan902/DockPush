from django.urls import path
from base.views import LoginAPIView, LogoutAPIView, SignupAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login_api'),
    path('logout/', LogoutAPIView.as_view(), name='logout_api'),
    path('signup/', SignupAPIView.as_view(), name='signup_api'),
]

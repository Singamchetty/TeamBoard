from django.urls import path

from .views import KBQueryView, LoginView, RegisterView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('kb/query/', KBQueryView.as_view(), name='kb-query'),
]

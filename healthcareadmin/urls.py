from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='healthcareAdminHome'),
    path('login/', views.login_user, name='healthcareAdminLogin'),
    path('healthcarereportpreview/', views.healthcarereportpreview, name='healthcarereportpreview'),
]
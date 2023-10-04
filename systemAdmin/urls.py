from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('medicalTech/profile', views.medicalTech_profile, name='medicalTech'),
    path('healthcareAdmin/profile', views.healthcareAdmin_profile, name='healthcareAdmin'),
    path('radiologyDoctor/profile', views.radiologyDoctor_profile, name='radiologyDoctor'),
    path('createAccount/', views.createAccount_view, name='createAccount'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('account/', views.systemAdmin_account, name='view_account'),
    path('createProfile/', views.create_profile, name='createProfile'),
    path('updateProfile/<int:pk>', views.update_profile, name='updateProfile'),
    path('updateAccount/<int:pk>', views.update_account,name='updateAccount'),
    path('suspendAccount/<int:pk>', views.suspend_account, name='suspendAccount'),
    path('unsuspendAccount/<int:pk>', views.unsuspend_account, name='unsuspendAccount'),
    path('suspendProfile/<int:pk>', views.suspend_profile, name='suspendProfile'),
    path('unsuspendProfile/<int:pk>', views.unsuspend_profile, name='unsuspendProfile'),
    path('profile_account/<int:pk>', views.specific_account, name='account'),
]

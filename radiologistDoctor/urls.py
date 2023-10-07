from django.urls import path, include
from . import views
from medicalTech import views as medical

urlpatterns = [
    path('', views.get_record, name='radiologistDoctorHome'),
    path('login/', views.login_user, name='radiologyDoctorLogin'),
    path('patient/<str:record_id>/', medical.get_data, name='patient_detail'),
    path('updateStatus/<str:record_id>/', views.update_status, name='update_status'),
    path('saveUpdate/<str:record_id>/', views.save_update,name='save_update'),
    path('save_notes/<str:record_id>/', views.saveNotes,name='save_notes'),
]
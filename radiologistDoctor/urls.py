from django.urls import path, include
from . import views
from medicalTech import views as medical

urlpatterns = [
    path('', views.get_record, name='radiologistDoctorHome'),
    path('login/', views.login_user, name='radiologyDoctorLogin'),
    path('patient/<str:record_id>/', medical.get_data, name='patient_detail'),
    path('createTemplates/', views.createTemplates, name='create_templates'),
    path('updateTemplates/<int:id>', views.updateTemplate, name='update_template'),
    path('deleteTemplates/<int:id>', views.deleteTemplate, name='delete_template'),
    path('updateImageFindings/<str:record_id>/',
         views.updateImageFindings, name='update_image_findings'),
]

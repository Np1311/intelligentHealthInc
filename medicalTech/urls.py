from django.urls import path
from . import views
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    path('home/', views.get_record, name='medical_tech_home'),
    path('login/', views.login_user, name='medical_tech_login'),
    path('registerPatient/', views.get_patient, name='register'),
    path('add_patient/', views.add_patient, name='add_patient'),
    path('update_request_time/', views.update_request_time, name='update_request'),
    path('patient/<str:record_id>/', views.get_data, name='get_data'),
    path('emergency/<str:record_id>/', views.emergency, name='emergency'),
    path('registered/<str:record_id>/', views.cancelEmergency, name='Registered'),
    path('patient/viewImage/<str:record_id>/',
         views.display_image, name='viewImage'),
    path('patient/save_image/<str:record_id>/',
         views.save_image, name='save_image_record'),
    path('patient/update/<str:record_id>/',
         views.update_image, name='update_image_record'),
    path('delete_images/', views.delete_images, name='delete_images'),
    path('delete_files/<str:record_id>', views.delete_file, name='delete_files'),
    path('update_record_status', views.update_record_status,
         name='updateRecordStatus'),
]

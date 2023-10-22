from django.shortcuts import render, redirect, get_object_or_404
from medicalTech.models import Image_Record,RadiologyRecord
from medicalTech.utils import DicomViewer
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from systemAdmin.models import profile
from django.contrib.auth.decorators import login_required
from .form import *
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

@csrf_protect
def login_user(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                user_profile = profile.objects.get(account=user.id)  # Assuming 'account' is the ForeignKey in Profile
                if user_profile.role == 'radiologyDoctor':
                   
                    login(request, user)
                    request.session['username'] = username
                    request.session['role'] = user_profile.role

                    if next_url is not None:
                        return redirect(next_url)
                    else:
                        return redirect('radiologistDoctorHome')
                    
                else:
                    messages.error(request, "You don't have the required role.")
                    return redirect('radiologyDoctorLogin')
            except profile.DoesNotExist:
                messages.error(request, "Invalid credentials.")
                return redirect('radiologyDoctorLogin')
        else:
            messages.error(request, "Invalid credentials or Your Account is Suspended.")
            return redirect('radiologyDoctorLogin')
    else:
        return render(request, 'login.html', {})

@login_required(login_url='radiologyDoctorLogin')
def get_record(request):
    records = Image_Record.records_with_images()
    templates = findingsTemplate.viewTemplate()
    path = request.path 

    return render(request, 'medical_home.html', {'records': records, 'templates':templates,'path': path})

# def update_status(request, record_id):
#     image_record = Image_Record.get_records(record_id)
#     image_bytes = image_record.image

#     image_stream = BytesIO(image_bytes)

#     content = DicomViewer(image_stream)
#     image = content.generate_image()

#     image_record.image=image

#     return render(request, 'update_status.html', {'image_data': image_record})

# def save_update(request, record_id):
#     if request.method == 'POST':
#         notes = request.POST.get("notes")
#         predictions = request.POST.get("predictions")

#         try:
#             # Get the corresponding RadiologyRecord instance
#             #record = RadiologyRecord.objects.get(record_id=record_id)
#             image_record = Image_Record.get_records(record_id)
#             if predictions:
#                 image_record.prediction = predictions
#                 image_record.notes = notes
#             else:
#                 # Create a new Image_Record instance without DICOM file
#                 image_record.notes = notes

#             image_record.save()

#             response_data = {"message": "Image and data saved successfully"}
#             return JsonResponse(response_data)
#         except RadiologyRecord.DoesNotExist:
#             response_data = {"message": "Record with the provided ID not found"}
#             return JsonResponse(response_data, status=400)
#         except Exception as e:
#             response_data = {"message": str(e)}
#             return JsonResponse(response_data, status=500)
#     else:
#         return JsonResponse({}, status=405)
    
# def saveNotes(request, record_id):
#     if request.method == 'POST':
#         notes = request.POST.get("notes")
    
#         try:
#             # Get the corresponding RadiologyRecord instance
#             #record = RadiologyRecord.objects.get(record_id=record_id)
#             image_record = Image_Record.get_records(record_id)
            
#             image_record.notes = notes

#             image_record.save()

#             response_data = {"message": "Image and data saved successfully"}
#             return JsonResponse(response_data)
#         except RadiologyRecord.DoesNotExist:
#             response_data = {"message": "Record with the provided ID not found"}
#             return JsonResponse(response_data, status=400)
#         except Exception as e:
#             response_data = {"message": str(e)}
#             return JsonResponse(response_data, status=500)
#     else:
#         return JsonResponse({}, status=405)
    

def createTemplates(request):
    if request.method == 'POST':
        form = FindingsTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            if 'username' in request.session:
                user = request.session.get('username')
            else :
                user = 'Guest'
            template.doctor = user  # Assuming there's a 'user' field in your FindingsTemplate model
            template.save()
            return redirect('radiologistDoctorHome')  # Redirect to a success page or wherever you want
    else:
        form = FindingsTemplateForm()

    return render(request, 'template_form.html', {'form': form, 'user': user})

def updateTemplate(request, id):
    template_instance = get_object_or_404(findingsTemplate, id=id)
    permission_denied = template_instance.doctor != request.session.get('user')
   
    
    if request.method == 'POST':
        form = UpdateTemplateForm(request.POST, instance=template_instance)
        if form.is_valid():
            form.save()
            return redirect('radiologistDoctorHome')
    else:
        form = UpdateTemplateForm(instance=template_instance)

    return render(request, 'template_form.html', {'form': form,'permission_denied': permission_denied})

@require_http_methods(["GET"])
def deleteTemplate(request, id):
    user = request.session.get('user')
    deletion_result, alert_message = findingsTemplate.deleteTemplateById(id,user)

    response_data = {
        'success': deletion_result,
        'message': alert_message
    }

    return JsonResponse(response_data)

def updateImageFindings(request, record_id):
    if request.method == 'POST':
        # Get the predictions and form data from the request
        predictions = request.POST.get('predictions')
        examination = request.POST.get('examination')
        findings = request.POST.get('findings')
        impressions = request.POST.get('impressions')
        if 'username' in request.session:
            user = request.session.get('username')
        else :
            user = 'Guest'
        # Perform the update operation in your model
        try:
            image_record = Image_Record.objects.get(record_id=record_id)
            radiology_record = RadiologyRecord.objects.get(record_id=record_id)
            image_record.predictions = predictions
            image_record.examination = examination
            image_record.findings = findings
            image_record.impressions = impressions
            image_record.radiologyDoctor = user
            radiology_record.status = 'Completed'
            image_record.save()
            radiology_record.save()
            response_data = {
                'success': True,
                'message': 'Successfully updated the image findings.',
            }
        except Image_Record.DoesNotExist:
            response_data = {
                'success': False,
                'message': 'Image record not found.',
            }
        except Exception as e:
            response_data = {
                'success': False,
                'message': f'Error: {str(e)}',
            }

        return JsonResponse(response_data)

    else:
       
        return JsonResponse({'success': False, 'message': 'Method Not Allowed'}, status=405)

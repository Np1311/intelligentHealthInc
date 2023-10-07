from django.shortcuts import render, redirect
from medicalTech.models import Image_Record,RadiologyRecord
from medicalTech.utils import DicomViewer
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from systemAdmin.models import profile
from django.contrib.auth.decorators import login_required

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
    path = request.path 

    return render(request, 'medical_home.html', {'records': records, 'path': path})

def update_status(request, record_id):
    image_record = Image_Record.get_records(record_id)
    image_bytes = image_record.image

    image_stream = BytesIO(image_bytes)

    content = DicomViewer(image_stream)
    image = content.generate_image()

    image_record.image=image

    return render(request, 'update_status.html', {'image_data': image_record})

def save_update(request, record_id):
    if request.method == 'POST':
        notes = request.POST.get("notes")
        predictions = request.POST.get("predictions")

        try:
            # Get the corresponding RadiologyRecord instance
            #record = RadiologyRecord.objects.get(record_id=record_id)
            image_record = Image_Record.get_records(record_id)
            if predictions:
                image_record.prediction = predictions
                image_record.notes = notes
            else:
                # Create a new Image_Record instance without DICOM file
                image_record.notes = notes

            image_record.save()

            response_data = {"message": "Image and data saved successfully"}
            return JsonResponse(response_data)
        except RadiologyRecord.DoesNotExist:
            response_data = {"message": "Record with the provided ID not found"}
            return JsonResponse(response_data, status=400)
        except Exception as e:
            response_data = {"message": str(e)}
            return JsonResponse(response_data, status=500)
    else:
        return JsonResponse({}, status=405)
    
def saveNotes(request, record_id):
    if request.method == 'POST':
        notes = request.POST.get("notes")
    
        try:
            # Get the corresponding RadiologyRecord instance
            #record = RadiologyRecord.objects.get(record_id=record_id)
            image_record = Image_Record.get_records(record_id)
            
            image_record.notes = notes

            image_record.save()

            response_data = {"message": "Image and data saved successfully"}
            return JsonResponse(response_data)
        except RadiologyRecord.DoesNotExist:
            response_data = {"message": "Record with the provided ID not found"}
            return JsonResponse(response_data, status=400)
        except Exception as e:
            response_data = {"message": str(e)}
            return JsonResponse(response_data, status=500)
    else:
        return JsonResponse({}, status=405)
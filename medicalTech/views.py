from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from systemAdmin.models import profile
from django.contrib.auth.decorators import login_required
from django.db import connection
import json
from django.http import JsonResponse, HttpResponse, FileResponse
from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from dateutil import parser
import uuid
from django.urls import reverse
from .utils import DicomViewer
import io
import zipfile
from django.shortcuts import get_object_or_404
from django.utils import timezone
from radiologistDoctor.form import ImageFindingsForm
from radiologistDoctor.models import findingsTemplate

# Create your views here.


@csrf_protect
def login_user(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                # Assuming 'account' is the ForeignKey in Profile
                user_profile = profile.objects.get(account=user.id)
                if request.session.get('role') == 'medicalTech' or user_profile.role == 'medicalTech':

                    login(request, user)
                    request.session['username'] = username
                    request.session['role'] = user_profile.role

                    if next_url is not None:
                        return redirect(next_url)
                    else:
                        return redirect('medical_tech_home')

                else:
                    messages.error(
                        request, "You don't have the required role.")
                    return redirect('medical_tech_login')
            except profile.DoesNotExist:
                messages.error(request, "Invalid credentials.")
                return redirect('medical_tech_login')
        else:
            messages.error(
                request, "Invalid credentials or Your Account is Suspended.")
            return redirect('medical_tech_login')
    else:
        return render(request, 'login.html', {})


def get_patient(request):
    # Fetch data from the HIS table using a raw SQL query
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM HIS;")
        his_data = cursor.fetchall()

    # You can process and manipulate the his_data here if needed

    # Pass the retrieved data to the template for rendering
    return render(request, 'HIS_display.html', {'his_data': his_data})


@csrf_protect
def add_patient(request):
    if request.method == 'POST':
        selected_rows_data = json.loads(request.POST.get('selectedRowsData'))

        for row_data in selected_rows_data:
            # Extract data from each row
            patient_id = row_data['patient_id']
            patient_name = row_data['name']
            date_of_birth_str = row_data['date_of_birth']
            nationality = row_data['nationality']
            area = row_data['area']
            gender = row_data['gender']

            try:
                # Try parsing the date using dateutil.parser
                date_of_birth = parser.parse(date_of_birth_str).date()
            except ValueError:
                # If parsing fails, handle the error (you might want to log or handle it differently)
                return JsonResponse({'message': 'Invalid date format'}, status=400)

            age = calculate_age(date_of_birth)

            senderDoctor = get_random_doctor_name()
            indications = 'fever, cough, nausea, shortness of breath, and diarrhea'
            # Create and save a new RadiologyRecord instance
            record = RadiologyRecord(
                record_id=generate_unique_id(),  # You need to define this function
                patient_id=patient_id,
                patient_name=patient_name,
                date_of_birth=date_of_birth,
                age=age,
                nationality=nationality,
                gender=gender,
                area=area,
                senderDoctor=senderDoctor,
                indications=indications
            )
            record.save()

        return JsonResponse({"message": "Records created successfully."})

    return JsonResponse({'message': 'Invalid request'}, status=400)


def calculate_age(date_of_birth):
    today = datetime.today().date()
    age = today.year - date_of_birth.year - \
        ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    return age


def generate_unique_id():
    unique_id = f"CXR{uuid.uuid4().int % 100000:05d}"
    return unique_id


@login_required(login_url='medical_tech_login')
def get_record(request):
    records = Image_Record.records_with_images()
    path = request.path
    if 'username' in request.session:
        user = request.session.get('username')
    else:
        user = 'Guest'

    return render(request, 'medical_home.html', {'records': records, 'path': path, 'user': user})


def get_random_doctor_name():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT DoctorName FROM Doctors ORDER BY RAND() LIMIT 1")
        random_doctor_name = cursor.fetchone()

    if random_doctor_name:
        return random_doctor_name[0]
    else:
        return None


def get_data(request, record_id):
    path = request.path
    if 'username' in request.session:
        user = request.session.get('username')
    else:
        user = 'Guest'
    try:
        record = RadiologyRecord.objects.get(record_id=record_id)
        image_record = None  # Initialize image_record variable

        try:
            image_record = Image_Record.objects.get(record_id=record)

            data_available = bool(
                image_record.examination or image_record.findings or image_record.impressions)
            image_available = bool(image_record.image)
            imageFilename_available = bool(image_record.image_filename)
            predictions_available = bool(image_record.prediction)

            if image_available:
                dicom_file = DicomViewer(io.BytesIO(image_record.image))
                image_record.image_data = dicom_file.generate_image()

            if predictions_available:
                predictions_value = image_record.prediction
            else:
                predictions_value = None

        except Image_Record.DoesNotExist:
            image_available = False
            predictions_available = False
            predictions_value = None
            data_available = None
            imageFilename_available = False

        if "radiologistDoctor" in path:
            try:
                covid_19_template = findingsTemplate.objects.get(doctor=user)

                initial_data = {
                    'findings': covid_19_template.template,
                    'impressions': 'Covid-19 Positive',
                }
            except findingsTemplate.DoesNotExist:
                initial_data = {
                    'findings': '',
                    'impressions': 'Covid-19 Positive',
                }

            image_form = ImageFindingsForm(
                predictions_value=predictions_value,
                data=data_available, instance=image_record, initial_data=initial_data
            )

        else:
            image_form = None

        context = {

            'record': record,
            'image_available': image_available,
            'imageFilename_available': imageFilename_available,
            'image_record': image_record,
            'path': path,
            'image_form': image_form,
            'predictions_available': predictions_available,  # Add the form to the context
        }
        return render(request, 'patient_detail.html', context)
    except RadiologyRecord.DoesNotExist:
        return render(request, 'record_not_found.html')


def emergency(request, record_id):

    RadiologyRecord.emergency(record_id)
    return redirect('medical_tech_home')


def cancelEmergency(request, record_id):

    RadiologyRecord.cancelEmergency(record_id)
    return redirect('medical_tech_home')


def update_request_time(request):
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        new_request_time_str = request.POST.get('new_request_time')

        try:
            record = RadiologyRecord.objects.get(record_id=record_id)
            new_request_time = timezone.make_aware(
                timezone.datetime.strptime(new_request_time_str, '%Y-%m-%dT%H:%M'))

            record.request_time = new_request_time
            record.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record.save()
            return JsonResponse({'success': True})
        except RadiologyRecord.DoesNotExist:
            return JsonResponse({'success': False})


def display_image(request, record_id):
    if request.method == "POST":
        dicom_file = request.FILES.get("dicom_file")

        if dicom_file:

            context = DicomViewer(dicom_file)

            image_data = context.generate_image()

            preprocess_image = context.preprocess_image()

            response_data = {"image_data": image_data,
                             "record_id": record_id, "preprocess_image": preprocess_image}
            return JsonResponse(response_data)
        else:
            response_data = {"message": "File upload failed"}
            return JsonResponse(response_data, status=400)
    else:
        return JsonResponse({}, status=405)


def save_image(request, record_id):
    if request.method == "POST":
        dicom_file = request.FILES.get("dicom_file")
        notes = request.POST.get("notes")
        image_filename = request.POST.get("filename")
        prediction = request.POST.get("prediction")
        prediction = prediction.strip()
        timestamp = request.POST.get("timestamp")

        if prediction is not None:
            prediction = prediction.strip()
        if 'username' in request.session:
            user = request.session.get('username')
        else:
            user = 'Guest'
        file_size = dicom_file.size
        file_size_mb = file_size / (1024 * 1024)
        print(file_size_mb)
        if file_size_mb < 15:
            try:
                # Get the corresponding RadiologyRecord instance
                record = RadiologyRecord.objects.get(record_id=record_id)

                if dicom_file:
                    binary_data = dicom_file.read()
                    image_record = Image_Record(record_id=record, image=binary_data, notes=notes,
                                                image_filename=image_filename, prediction=prediction, upload_date=timestamp, medTech=user)
                    if record.status != 'EMERGENCY':
                        record.status = 'In Progress'
                    record.save()
                else:
                    # Create a new Image_Record instance without DICOM file
                    image_record = Image_Record(record_id=record, notes=notes)

                image_record.save()

                response_data = {
                    "message": "Image and data saved successfully"}
                return JsonResponse(response_data)
            except RadiologyRecord.DoesNotExist:
                response_data = {
                    "message": "Record with the provided ID not found"}
                return JsonResponse(response_data, status=400)
            except Exception as e:
                response_data = {"message": str(e)}
                return JsonResponse(response_data, status=500)
        else:
            response_data = {"message": "File size exceeded"}
            return JsonResponse(response_data)
    else:
        return JsonResponse({}, status=405)


def update_image(request, record_id):
    if request.method == "POST":
        dicom_file = request.FILES.get('dicom_file', None)
        notes = request.POST.get("notes")
        image_filename = request.POST.get("filename")
        prediction = request.POST.get("prediction")
        if prediction is not None:
            prediction = prediction.strip()
        timestamp = request.POST.get("timestamp")
        if 'username' in request.session:
            user = request.session.get('username')
        else:
            user = 'Guest'

        try:
            # Get the corresponding RadiologyRecord instance
            image_record = Image_Record.get_records(record_id)
            if dicom_file:
                binary_data = dicom_file.read()
                image_record.image_filename = image_filename
                image_record.image = binary_data
                image_record.prediction = prediction
                image_record.upload_date = timestamp
                image_record.notes = notes
                image_record.medTech = user
            else:
                # Create a new Image_Record instance without DICOM file
                image_record.notes = notes

            image_record.save()

            response_data = {"message": "Image and data saved successfully"}
            return JsonResponse(response_data)
        except RadiologyRecord.DoesNotExist:
            response_data = {
                "message": "Record with the provided ID not found"}
            return JsonResponse(response_data, status=400)
        except Exception as e:
            response_data = {"message": str(e)}
            return JsonResponse(response_data, status=500)
    else:
        return JsonResponse({}, status=405)


def delete_images(request):
    if request.method == "POST":
        try:
            selected_ids_json = request.body.decode('utf-8')
            selected_ids = json.loads(selected_ids_json)

            message = Image_Record.delete_records_by_ids(selected_ids)

            return HttpResponse(content=message, status=200)
        except json.JSONDecodeError:
            return HttpResponse(status=400, content="Invalid JSON data in the request body")
    else:
        return HttpResponse(status=405, content="Method not allowed")


def delete_file(request, record_id):
    if request.method == 'GET':
        image_record = get_object_or_404(Image_Record, record_id=record_id)

        # Delete the file and filename
        image_record.image = None
        image_record.deletion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_record.save()

        return JsonResponse({'message': 'File deleted successfully'})
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)


def update_record_status(request):
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        new_status = request.POST.get('new_status')

        try:
            record = RadiologyRecord.objects.get(record_id=record_id)
            record.status = new_status
            record.save()

            return JsonResponse({'success': True})
        except RadiologyRecord.DoesNotExist:

            return JsonResponse({'success': False, 'message': 'Record does not exist'})

    return JsonResponse({'success': False, 'message': 'Invalid HTTP method'})

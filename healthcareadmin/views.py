from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from medicalTech.models import Image_Record,RadiologyRecord
from django.http import JsonResponse, HttpResponse
from django.template import loader
from datetime import datetime
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
                if user_profile.role == 'healthcareAdmin':
                   
                    login(request, user)

                    if next_url is not None:
                        return redirect(next_url)
                    else:
                        return redirect('healthcareAdminHome')
                    
                else:
                    messages.error(request, "You don't have the required role.")
                    return redirect('healthcareAdminLogin')
            except profile.DoesNotExist:
                messages.error(request, "Invalid credentials.")
                return redirect('healthcareAdminLogin')
        else:
            messages.error(request, "Invalid credentials or Your Account is Suspended.")
            return redirect('healthcareAdminLogin')
    else:
        return render(request, 'login.html', {})
    
@login_required(login_url='healthcareAdminLogin')    
def home(request):
    
    from_date = request.GET.get('fromDate')
    to_date = request.GET.get('toDate')

    
    if from_date and to_date:
        patients_list = Image_Record.records_with_images().filter(
            Q(upload_date__date__gte=from_date) &
            Q(upload_date__date__lte=to_date)
        )
    else:
        patients_list = Image_Record.records_with_images()

   
    paginator = Paginator(patients_list, 10)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)

    return render(request, 'healthcareadminhome.html', {'patients': page})

def healthcarereportpreview(request):
    def get_queryset(from_date,to_date):
        RadiologyRecord.positive_record(from_date, to_date)

        record_instance = RadiologyRecord()

        area_data = record_instance.area_data()
        nationality_data = record_instance.nationality_data()
        visit_data = record_instance.visit_data(from_date, to_date)
        age_data = record_instance.age_data()
        total_covid = record_instance.total_covid_data()




        response_data = {
            'total_covid': total_covid,
            'area_data': area_data,
            'nationality_data': nationality_data,
            'visit_data': visit_data,
            'age_data': age_data,
        }
        return response_data
    
    if request.GET:
        from_date_str = request.GET.get('fromDate')
        to_date_str = request.GET.get('toDate')

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

            response_data = get_queryset(from_date, to_date)

            return JsonResponse(response_data)
           
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'})
    else:
        from_date = None
        to_date = None

        response_data = get_queryset(from_date, to_date)

        return render(request, 'healthcarereportpreview.html', {'data': response_data})
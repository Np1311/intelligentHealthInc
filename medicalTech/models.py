from django.db import models
from django.db import transaction
from collections import Counter
from datetime import timedelta, datetime


# Create your models here.
class RadiologyRecord(models.Model):
    # Unique ID that starts with CXR
    record_id = models.CharField(max_length=20, primary_key=True)

    # Patient information
    patient_name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    date_of_birth = models.DateField()

    area = models.CharField(max_length=255)
    nationality = models.CharField(max_length=255)

    # Imaging study details
    modality = models.CharField(max_length=50, default='CXR')
    request_time = models.DateTimeField(null=True)

    senderDoctor = models.CharField(max_length=255, default=None)
    indications = models.TextField(null=True)
    update_time = models.DateTimeField(null=True)
    # Additional information

    # Status of the record
    STATUS_CHOICES = (
        ('Registered', 'Registered'),
        ('Queueing', 'Queueing'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('EMERGENCY', 'EMERGENCY'),
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Registered')

    filtered_records = None

    def __str__(self):
        return self.record_id

    @classmethod
    def view_records(cls):
        return cls.objects.all()

    @classmethod
    def get_records_by_record_id(cls, id):
        records = cls.objects.filter(record_id=id)
        return records

    @classmethod
    def emergency(cls, id):
        try:
            record = cls.objects.get(record_id=id)
            # Assuming you want to update the request_time to the current datetime
            record.status = 'EMERGENCY'
            record.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record.save()
        except cls.DoesNotExist:
            raise ValueError(f"Record with id {id} not found")

    @classmethod
    def cancelEmergency(cls, id):
        try:
            record = cls.objects.get(record_id=id)
            # Assuming you want to update the request_time to the current datetime
            record.status = 'Registered'
            record.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record.save()
        except cls.DoesNotExist:
            raise ValueError(f"Record with id {id} not found")

    @classmethod
    def positive_record(self, from_date, to_date):

        if (from_date and to_date):
            image_records = Image_Record.objects.filter(
                prediction='Positive',
                upload_date__range=[from_date, to_date],
            )

            positive_record_ids = image_records.values('record_id')

            self.filtered_records = Image_Record.records_with_images().filter(
                record_id__in=positive_record_ids,
            )

            return self.filtered_records
        else:
            image_records = Image_Record.objects.filter(
                prediction='Positive',
            )

            positive_record_ids = image_records.values('record_id')

            self.filtered_records = Image_Record.records_with_images().filter(
                record_id__in=positive_record_ids,
            )

            print(self.filtered_records)

            return self.filtered_records

    def area_data(self):

        if self.filtered_records is not None:
            area_data = list(
                self.filtered_records.values_list('area', flat=True))
            data_counter = Counter(area_data)

            labels = list(data_counter.keys())
            data = list(data_counter.values())

            return {
                'labels': labels,
                'data': data
            }

        else:
            return []

    def nationality_data(self):
        if self.filtered_records is not None:
            nationality_data = list(
                self.filtered_records.values_list('nationality', flat=True))
            data_counter = Counter(nationality_data)

            labels = list(data_counter.keys())
            data = list(data_counter.values())

            return {
                'labels': labels,
                'data': data
            }
        else:
            return []

    def age_data(self):
        if self.filtered_records is not None:
            age_data = list(
                self.filtered_records.values_list('age', flat=True))
            age_ranges = [(0, 10), (11, 20), (21, 30), (31, 40),
                          (41, 50), (51, 60), (61, float('inf'))]
            age_labels = ['<10', '11-20', '21-30',
                          '31-40', '41-50', '51-60', '>60']
            age_counts = {label: 0 for label in age_labels}

            for age in age_data:
                for i, (start, end) in enumerate(age_ranges):
                    if start <= age <= end:
                        age_counts[age_labels[i]] += 1
                        break

            data = [age_counts[label] for label in age_labels]

            return {
                'labels': age_labels,
                'data': data
            }
        else:
            return []

    def visit_data(self, from_date, to_date):
        if self.filtered_records is not None:
            visit_data = list(self.filtered_records.values_list(
                'request_time', flat=True))
            visit_counts = {}

            visit_data = [value for value in visit_data if value is not None]

            if from_date is None or to_date is None:
                # If from_date or to_date is None, use the date range from filtered records
                if visit_data:
                    min_date = min(visit_data).date()
                    max_date = max(visit_data).date()
                    current_date = min_date

                    while current_date <= max_date:
                        next_week_start = current_date + \
                            timedelta(days=(7 - current_date.weekday()))
                        week_label = f"{current_date.strftime('%d-%m-%Y')} to {next_week_start.strftime('%d-%m-%Y')}"
                        visit_counts[week_label] = 0
                        current_date = next_week_start
                else:
                    return []

            else:
                current_date = from_date
                # Include the end date in the range
                to_date = to_date + timedelta(days=1)
                while current_date <= to_date:
                    next_week_start = current_date + \
                        timedelta(days=(7 - current_date.weekday()))
                    week_label = f"{current_date.strftime('%d-%m-%Y')} to {next_week_start.strftime('%d-%m-%Y')}"
                    visit_counts[week_label] = 0
                    current_date = next_week_start

            for visit_time in visit_data:
                visit_time = visit_time.date()  # Extract only the date part
                for week_label, week_start in visit_counts.items():
                    week_start = datetime.strptime(
                        week_label.split(' ')[0], '%d-%m-%Y').date()
                    week_end = datetime.strptime(
                        week_label.split(' ')[-1], '%d-%m-%Y').date()
                    if week_start <= visit_time < week_end:
                        visit_counts[week_label] += 1
                        break

            labels = list(visit_counts.keys())
            data = list(visit_counts.values())

            return {
                'labels': labels,
                'data': data
            }
        else:
            return []

    def total_covid_data(self):
        if self.filtered_records is not None:
            total_records_count = self.filtered_records.count()
            return total_records_count
        else:
            return 0


class Image_Record(models.Model):
    record_id = models.OneToOneField(
        RadiologyRecord, on_delete=models.CASCADE, primary_key=True)

    image = models.BinaryField(null=True)
    image_filename = models.CharField(max_length=255, default="None")

    prediction = models.CharField(max_length=50, null=True)

    notes = models.TextField(blank=True)

    upload_date = models.DateTimeField(null=True)

    examination = models.CharField(max_length=255, null=True)

    findings = models.TextField(blank=True, null=True)

    impressions = models.CharField(max_length=255, null=True)

    medTech = models.CharField(max_length=255, null=True)

    radiologyDoctor = models.CharField(max_length=255, null=True)

    deletion_time = models.DateTimeField(null=True)

    @classmethod
    def get_records(cls, id):
        image_records = cls.objects.get(record_id=id)
        return image_records

    @classmethod
    def get_notes(cls, id):
        try:
            data = cls.objects.get(record_id=id)
            return data.notes
        except cls.DoesNotExist:
            return None

    @classmethod
    def records_with_images(cls):
        return RadiologyRecord.objects.select_related('image_record').annotate(
            status_order=models.Case(
                models.When(status='EMERGENCY', then=models.Value(0)),
                models.When(status='Queueing', then=models.Value(1)),
                models.When(status='Registered', then=models.Value(2)),
                models.When(status='In Progress', then=models.Value(3)),
                default=models.Value(4),
                output_field=models.IntegerField()
            ),
            request_time_order=models.F('request_time')
        ).order_by('status_order', 'request_time_order')

    @classmethod
    def delete_records_by_ids(cls, record_ids):
        message = ""
        try:
            with transaction.atomic():
                queryset = cls.objects.filter(record_id__in=record_ids)
                currentDatetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                queryset.update(image=None, deletion_time=currentDatetime)
                message = f"Successfully deleted record(s)."
        except Exception as e:
            message = f"Error deleting records: {str(e)}"

        return message

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User


# Create your models here.
class profile (models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('suspend', 'Suspended'),
    )
    role_choices = (
        ('systemAdmin', 'System Admin'),
        ('medicalTech', 'Medical Technician'),
        ('healthcareAdmin', 'Healthcare Admin'),
        ('radiologyDoctor', 'Radiology Doctor'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    dob = models.DateField()
    phone = PhoneNumberField(region='SG')
    account = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active')
    role = models.CharField(
        max_length=50, choices=role_choices, default='systemAdmin')

    @classmethod
    def filterProfileByRole(cls, role):
        profiles = cls.objects.filter(role=role)
        return profiles

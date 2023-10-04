from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User
from django import forms
from .models import profile
from phonenumber_field.formfields import PhoneNumberField
from django.http import QueryDict
from django.urls import resolve


class CreateAccountForm(UserCreationForm):
    first_name = forms.CharField(label="", max_length=100,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=100,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Last Name'}))

    class Meta: 
        model = User
        fields = ('username','first_name','last_name','password1','password2')
    def __init__(self, *args, **kwargs):
        super(CreateAccountForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
       
        latest_user_data = kwargs.pop('latest_user_data', None)

        super(CreateProfileForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name == 'dob':
                field.widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                field.help_text = 'Please enter your date of birth in the format YYYY-MM-DD.'
            elif field_name == 'phone':
                field.widget = forms.TextInput(attrs={'class': 'form-control', })
                field.help_text = 'Please enter your phone number format, such as 6234 5678.'
            elif field_name in ['account', 'role', 'status']:
                field.widget.attrs.update({'class': 'form-control dropdown-arrow', 'style': 'background-color: white; color: black;'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        
        if latest_user_data:
            self.initial['account'] = latest_user_data['username']
            self.initial['first_name'] = latest_user_data['first_name']
            self.initial['last_name'] = latest_user_data['last_name']

class update_profile_form(forms.ModelForm):
    class Meta:
        model = profile
        fields = '__all__'

    def __init__(self, *args, instance=None, **kwargs):
        super(update_profile_form, self).__init__(instance=instance, *args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name == 'dob':
                field.widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                field.help_text = 'Please enter your date of birth in the format YYYY-MM-DD.'
            elif field_name == 'phone':
                field.widget = forms.TextInput(attrs={'class': 'form-control', })
                field.help_text = 'Please enter your phone number format, such as 6234 5678.'
            elif field_name in ['account', 'role', 'status']:
                field.widget.attrs.update({'class': 'form-control dropdown-arrow', 'style': 'background-color: white; color: black;'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        if instance:
            # Filter out users who already have profiles, except for the user associated with instance ID
            existing_user_ids = profile.objects.values_list('account', flat=True)
            self.fields['account'].queryset = User.objects.filter(id=instance.account.id) | User.objects.exclude(id__in=existing_user_ids)

class Update_Account_Form(UserChangeForm):
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    is_staff = forms.BooleanField(label="Staff Status ", required=False)
    is_active = forms.BooleanField(label="Active:", required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'is_staff', 'is_active')

    def __init__(self, *args, **kwargs):
        super(Update_Account_Form, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['username'].label = ''

        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['first_name'].label = ''

        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['last_name'].label = ''

        self.fields['is_staff'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'

        # Remove the password field from the widget
        self.fields['password'].widget = forms.HiddenInput()
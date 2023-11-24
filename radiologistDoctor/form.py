from django import forms
from .models import findingsTemplate
from medicalTech.models import *


class FindingsTemplateForm(forms.ModelForm):
    class Meta:
        model = findingsTemplate
        fields = ['template_name', 'template']
    template_name = forms.CharField(
        label='Template Name', initial='Covid-19', disabled=True)


class UpdateTemplateForm(forms.ModelForm):
    class Meta:
        model = findingsTemplate
        fields = ['template_name', 'template']

    def __init__(self, *args, **kwargs):
        super(UpdateTemplateForm, self).__init__(*args, **kwargs)

        # Access the instance being updated
        instance = kwargs.get('instance')

        # Fill in the initial values for the fields
        if instance:
            self.fields['template_name'].initial = instance.template_name
            self.fields['template'].initial = instance.template


class ImageFindingsForm(forms.ModelForm):
    class Meta:
        model = Image_Record
        fields = ['examination', 'findings', 'impressions']
    examination = forms.CharField(label='Examination', initial='CHEST (PA)')
    findings = forms.CharField(label='Findings', widget=forms.Textarea)
    impressions = forms.CharField(label='Impressions', initial='Normal')

    def __init__(self, *args, predictions_value=None, data=None, initial_data=None, instance=None, **kwargs):

        super().__init__(*args, **kwargs)

        if data:
            self.fields['examination'].initial = instance.examination
            self.fields['findings'].initial = instance.findings
            self.fields['impressions'].initial = instance.impressions

        else:
            if predictions_value == 'Positive':
                # Fetch the initial value from the database

                self.fields['findings'].initial = initial_data.get('findings')
                self.fields['impressions'].initial = initial_data.get(
                    'impressions')

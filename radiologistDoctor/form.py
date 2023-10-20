from django import forms
from .models import findingsTemplate
from medicalTech.models import *

class FindingsTemplateForm(forms.ModelForm):
    class Meta:
        model = findingsTemplate
        fields = ['template_name', 'template']

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
    findings = forms.CharField(label='Findings', widget=forms.Textarea, initial='')
    impressions = forms.CharField(label='Impressions', initial='Normal')

    def __init__(self, *args, predictions_value=None,data = None, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if data:
            self.fields['examination'].initial = instance.examination
            self.fields['findings'].initial = instance.findings
            self.fields['impressions'].initial = instance.impressions
        # Check the condition to set the initial value
        else:
            if predictions_value == 'Positive':
                # Fetch the initial value from the database
                covid_19_template = findingsTemplate.objects.get(template_name='Covid-19')
                self.fields['findings'].initial = covid_19_template.template
                self.fields['impressions'].initial ='Covid-19 Positive'
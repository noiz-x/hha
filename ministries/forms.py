from django import forms
from django.core.validators import RegexValidator, EmailValidator
from core.models import Worker
from ministries.models import Department

class NewWorkerForm(forms.ModelForm):

    name = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'h-full-width h-remove-bottom', 'placeholder': 'Your Name'}),
        validators=[RegexValidator(r'^[a-zA-Z\s]*$', message='Name should only contain letters and spaces.')],
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'h-full-width h-remove-bottom', 'placeholder': 'Phone Number'}),
        validators=[RegexValidator(r'^\+234\d{10}$', message='Invalid phone number format. Please use +234XXXXXXXXXX.')],
    )
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(attrs={'class': 'h-full-width h-remove-bottom', 'placeholder': 'Email'}),
        validators=[EmailValidator(message='Enter a valid email address.')],
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.exclude(name__iexact='Pastorates'),
        widget=forms.Select(attrs={'class': 'h-full-width h-remove-bottom'}),
        empty_label=None,
    )
    question = forms.ChoiceField(
        choices=(
            ('yes', 'Yes'),
            ('no', 'No'),
        ),
        initial='yes',
        widget=forms.Select(attrs={'class': 'h-full-width h-remove-bottom'}),
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'h-full-width h-remove-bottom', 'placeholder': 'Comments & Questions'}),
        required=False,
    )

    class Meta:
        model = Worker
        fields = ['name', 'phone_number', 'email', 'department', 'question', 'comment']

from django import forms
from django.core.validators import RegexValidator, EmailValidator
from demographic.models import Demographic

class NewDemographicForm(forms.Form):

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
    demographic = forms.ModelChoiceField(
        queryset=Demographic.objects.all(),
        widget=forms.Select(attrs={'class': 'h-full-width h-remove-bottom'}),
        empty_label=None,
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'h-full-width h-remove-bottom', 'placeholder': 'Comments & Questions'}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        slug = kwargs.pop('slug', None)
        super().__init__(*args, **kwargs)

        if slug:
            try:
                demographic = Demographic.objects.get(slug=slug)
                self.fields['demographic'].queryset = Demographic.objects.filter(name=demographic.name)
                self.fields['demographic'].initial = demographic
            except Demographic.DoesNotExist:
                pass

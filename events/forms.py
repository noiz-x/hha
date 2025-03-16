from django import forms
from django.core.validators import RegexValidator, EmailValidator
from events.models import Event, Registration
from PIL import Image

class NewRegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['name', 'phone_number', 'event', 'comment']

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
        error_messages={'invalid': 'Enter a valid email address.'},
    )
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
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
                event = Event.objects.get(slug=slug)
                self.fields['event'].queryset = Event.objects.filter(name=event.name)
                self.fields['event'].initial = event
            except Event.DoesNotExist:
                pass


class NewRegistrationFormwithProof(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['name', 'phone_number', 'event', 'comment']

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
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        widget=forms.Select(attrs={'class': 'h-full-width h-remove-bottom'}),
        empty_label=None,
    )
    proof = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'h-full-width h-remove-bottom'}),
        required=False,
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
                event = Event.objects.get(slug=slug)
                self.fields['event'].queryset = Event.objects.filter(name=event.name)
                self.fields['event'].initial = event
            except Event.DoesNotExist:
                pass

    def clean_proof(self):
        proof = self.cleaned_data.get('proof')
        if proof:
            try:
                img = Image.open(proof)
                if img.format.lower() not in ['jpeg', 'png', 'gif']:
                    raise forms.ValidationError('Please upload a valid JPEG, PNG, or GIF image.')
            except (IOError, AttributeError):
                raise forms.ValidationError('Please upload a valid image file.')
        else:
            raise forms.ValidationError('Please upload payment proof.')

        return proof

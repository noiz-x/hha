import uuid
from django.core.validators import RegexValidator
from django.db import models

class Worker(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?234\d{10}$', 'Invalid phone number format. Please use +234XXXXXXXXXX.')],
    )
    email = models.EmailField()
    unique_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    confirmed = models.BooleanField(default=False)
    department = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Leader(models.Model):
    worker = models.OneToOneField(Worker, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(upload_to='leaders/', default='leaders/default.png')

    def __str__(self):
        return self.worker.name

class InspirationalQuote(models.Model):
    quote = models.TextField()
    speaker = models.CharField(max_length=200)

    def __str__(self):
        return self.speaker
import uuid
from datetime import timedelta, datetime
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from demographic.models import Demographic
import recurrence.fields  # django-recurrence

class Event(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, editable=False)
    is_special = models.BooleanField(default=False)
    rsvp_form_needed = models.BooleanField(
        default=False,
        help_text=(
            'If selected, a registration form will be produced.<br>'
            'Note: Used only when special is selected.'
        )
    )
    payment_upload_needed = models.BooleanField(
        default=False,
        help_text=(
            'If selected, payment would be required for registration.<br>'
            'Note: Used only when RSVP form is selected.'
        )
    )
    speakers = models.TextField(
        blank=True, 
        null=True, 
        help_text=(
            'Provide the names of speakers, separated by \', \'.<br>'
            'Note that this is only applicable when the \'special\' field is selected.'
        )
    )
    hashtags = models.TextField(
        blank=True, 
        null=True,
        help_text=(
            'All hashtags should be separated by spaces, like this: \'#GOD #JESUS\'. '
            'Please note that this format is only used when the \'special\' field is selected.'
        )
    )
    description = models.TextField(blank=True, null=True)
    # Use django-recurrence for repeat rules.
    recurrence = recurrence.fields.RecurrenceField(
        null=True,
        blank=True,
        help_text="Set recurrence rules for the event. Leave empty for one-time events."
    )
    demographic = models.ForeignKey(Demographic, on_delete=models.CASCADE, blank=True, null=True)
    start_time = models.TimeField(help_text='Start time of the event.', default=timezone.now)
    end_time = models.TimeField(help_text='End time of the event.', default=timezone.now)
    location = models.CharField(max_length=200, help_text='Location of the event.')
    image = models.ImageField(upload_to='event/', blank=True, null=True)
    link = models.URLField(
        blank=True,
        null=True,
        help_text='Keep this space empty until the live link is obtained.'
    )

    def delete(self, *args, **kwargs):
        if self.image:
            storage, path = self.image.storage, self.image.path
            storage.delete(path)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        # Occurrence generation is handled on the fly via the recurrence field.

    def get_occurrences(self, range_start, range_end):
        """
        Returns a list of datetime objects representing event occurrences
        between 'range_start' and 'range_end'. For recurring events, uses the
        recurrence field; for one-time events, returns the start_date if it lies within the range.
        """       
        if self.recurrence:
            return self.recurrence.between(
                range_start,
                range_end,
                dtstart=range_start,
                # inc=True
            )
        elif range_start <= self.start_date <= range_end:
            return [self.start_date]
        return []

    def get_paragraphs(self):
        return self.description.split('\r\n\r\n\r\n') if self.description else []

    def get_speakers(self):
        return self.speakers.split(', ') if self.speakers else []

    def get_hashtags(self):
        return self.hashtags.split(' ') if self.hashtags else []

    def __str__(self):
        return self.name

class Registration(models.Model):
    name = models.CharField(max_length=100)
    unique_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(max_length=20)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    proof = models.ImageField(upload_to='registration/', blank=True)
    comment = models.TextField()
    confirmed = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        if self.proof:
            storage, path = self.proof.storage, self.proof.path
            storage.delete(path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.event.name}"

class QRCodeToken(models.Model):
    user = models.ForeignKey(Registration, on_delete=models.CASCADE)
    token = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.name

    def is_valid(self):
        return (
            not self.used and
            (self.created_at + timedelta(hours=24)) >= timezone.now().astimezone(timezone.get_current_timezone())
        )

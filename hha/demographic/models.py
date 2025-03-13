from django.db import models
from django.utils.text import slugify
from core.models import Leader

class Demographic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    description = models.TextField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class DemographicLeader(models.Model):
    leader = models.ForeignKey(Leader, on_delete=models.CASCADE)
    demographic = models.ForeignKey(Demographic, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.leader.worker.name} - {self.demographic.name}"


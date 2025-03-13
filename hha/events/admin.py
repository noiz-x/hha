from django.contrib import admin
from events.models import Event, Registration, QRCodeToken#, EventDate

admin.site.register(Event)
# admin.site.register(EventDate)
admin.site.register(Registration)
admin.site.register(QRCodeToken)

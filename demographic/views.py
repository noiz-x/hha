from datetime import timedelta, datetime
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from demographic.forms import NewDemographicForm
from demographic.models import Demographic, DemographicLeader
from events.models import Event


def home(request):
    demographics = Demographic.objects.all()

    context = {
        'demographics': demographics,
    }
    return render(request, 'demographic/demographics.html', context)

def single(request, slug):
    context = {}
    now = timezone.now()
    two_months_later = now + timedelta(days=60)

    demographic_leader = DemographicLeader.objects.get(demographic__slug=slug)

    events = Event.objects.filter(demographic__slug=slug).order_by('start_time')
    
    # Build a list of upcoming occurrences
    upcoming_occurrences = []
    for event in events:
        occ_dates = event.get_occurrences(range_start=now, range_end=two_months_later)
        for occ in occ_dates:
            # Compute the end time based on the event duration
            upcoming_occurrences.append({
                'event': event,               # Parent event details
                'date': occ.date(),           # Occurrence date
            })
    
    # Sort the occurrences by date and time (earliest first)
    upcoming_occurrences.sort(key=lambda x: (x['date'], x['event'].start_time))

    if request.method == 'POST':
        form = NewDemographicForm(request.POST, slug=slug)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            name = cleaned_data['name']
            phone_number = cleaned_data['phone_number']
            email = cleaned_data['email']
            demographic = cleaned_data['demographic']
            comment = cleaned_data['comment']

            email_context = {
                'name': name,
                'phone_number': phone_number,
                'email': email,
                'demographic': demographic,
                'comment': comment,
            }

            email_subject = 'Connect Group'
            email_body_text = render_to_string('demographic/email/demographic_notification.txt', email_context)
            email_body_html = render_to_string('demographic/email/demographic_notification.html', email_context)

            send_mail(
                email_subject,
                strip_tags(email_body_text),
                'hopehallassembly@gmail.com',
                ['hopehallassembly@gmail.com'],
                html_message=email_body_html,
                fail_silently=False,
            )

            return render(request, 'demographic/success.html')
        else:
            context.update({'form': form, 'goto': '#error'})

    else:
        form = NewDemographicForm(slug=slug)

    context.update({
        'demographic_leader': demographic_leader,
        'form': form,
        'events': upcoming_occurrences,
    })
    return render(request, 'demographic/demographics-single.html', context)

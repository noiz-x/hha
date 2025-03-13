import io
import qrcode
import secrets
import uuid
from datetime import timedelta, datetime, time
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from events.forms import NewRegistrationForm, NewRegistrationFormwithProof
from events.models import Event, Registration, QRCodeToken


def get_occurrence_for_date(event, target_date):
    """
    Given an event instance and a target_date (a date object),
    returns the first occurrence (as a datetime object) that falls
    within that day, or None if no occurrence is found.
    """
    # Define the start and end of the target day
    day_start = datetime.combine(target_date, time.min)
    day_end = datetime.combine(target_date, time.max)
    
    # Use the event's get_occurrences method to retrieve occurrences within the day
    occurrences = event.get_occurrences(day_start, day_end)
    print(event)
    
    # Return the first occurrence if available
    if occurrences:
        return occurrences[0]
    return None
    

def home(request):
    now = timezone.now()
    print(now)
    two_months_later = now + timedelta(days=60)
    
    # Retrieve all events (you can add filtering if needed)
    events = Event.objects.all().order_by('start_time')
    
    # Build a list of upcoming occurrences
    upcoming_occurrences = []
    for event in events:
        occ_dates = event.get_occurrences(now, two_months_later)
        for occ in occ_dates:
            # Compute the end time based on the event duration
            upcoming_occurrences.append({
                'event': event,               # Parent event details
                'date': occ.date(),           # Occurrence date
            })
    
    # Sort the occurrences by date and time (earliest first)
    upcoming_occurrences.sort(key=lambda x: (x['date'], x['event'].start_time))
    
    # Paginate the occurrences list (6 per page)
    paginator = Paginator(upcoming_occurrences, 6)
    page = request.GET.get('page', 1)
    try:
        occurrence_page = paginator.page(page)
    except EmptyPage:
        occurrence_page = paginator.page(paginator.num_pages)

    context = {'events': occurrence_page}
    return render(request, 'events/events.html', context)


def all_events(request):
    now = timezone.now()
    two_months_later = now + timedelta(days=60)
    six_months_ago = now - timedelta(days=3600)
    
    events = Event.objects.all().order_by('start_time')
    
    # Build a list of occurrences for each event with complete details
    event_occurrences = []
    for event in events:
        occ_dates = event.get_occurrences(six_months_ago, two_months_later)
        for occ in occ_dates:
            event_occurrences.append({
                'event': event,
                'date': occ.date(),
            })
    
    # Optionally sort occurrences by occurrence time
    event_occurrences.sort(key=lambda x: (x['date'], x['event'].start_time))
    
    # Paginate the occurrences (e.g., 6 per page)
    paginator = Paginator(event_occurrences, 6)
    page = request.GET.get('page', 1)
    try:
        occurrence_page = paginator.page(page)
    except EmptyPage:
        occurrence_page = paginator.page(paginator.num_pages)

    context = {
        'events': occurrence_page,
    }
    return render(request, 'events/events-all.html', context)

def single(request, slug, date):
    event = get_object_or_404(Event, slug=slug)

    now = timezone.now()
    two_months_later = now + timedelta(days=60)
    six_months_ago = now - timedelta(days=3600)

    day_start = datetime.combine(datetime.strptime(date, '%Y-%m-%d').date(), time.min)

    
    # Retrieve the occurrence for this event on the target date
    occurrences = []
    occ_dates = event.get_occurrences(six_months_ago, two_months_later)
    for occ in occ_dates:
        if occ.date() == day_start.date():
            occurrences.append({
                'event': event,
                'date': occ.date(),
            })

    share_url = request.build_absolute_uri()
    current_datetime = timezone.now()
    context = {}

    if occurrences[0]['date'] < current_datetime.date() or (occurrences[0]['date'] == current_datetime.date() and occurrences[0]['event'].start_time < (current_datetime + timedelta(hours=1)).time()):
        form_enabled = False
        share_url_enabled = False
    else:
        form_enabled = True
        share_url_enabled = True

    if occurrences[0]['event'].is_special:
        if occurrences[0]['event'].rsvp_form_needed:
            form_cls = NewRegistrationFormwithProof if occurrences[0]['event'].payment_upload_needed else NewRegistrationForm
            form = form_cls(request.POST, request.FILES, slug=slug) if request.method == 'POST' else form_cls(slug=slug)
        else:
            form = None

        if request.method == 'POST':
            if form.is_valid():
                cleaned_data = form.cleaned_data
                name = cleaned_data['name']
                try:
                    first_name, last_name = name.split()
                    swapped_name = f"{last_name} {first_name}"
                except ValueError:
                    form.add_error('name', 'Please provide a full name.')
                    return render(request, 'events/special-events-single.html', {'form': form, 'goto': '#error'})

                unique_uuid = uuid.uuid4()
                form.fields['unique_uuid'] = forms.CharField(widget=forms.HiddenInput, initial=unique_uuid)

                email_context = {
                    'protocol': request.scheme,
                    'domain': request.get_host(),
                    'unique_uuid': unique_uuid,
                    **cleaned_data,
                }

                existing = Registration.objects.filter(
                    Q(name__iexact=name) |
                    Q(name__iexact=swapped_name)
                ).first()

                if existing:
                    form.add_error('name', 'You are already registered.')
                    return render(request, 'events/special-events-single.html', {'form': form, 'goto': '#error'})

                email_subject = 'Event Registration'
                email_body_text = render_to_string('events/email/events_registration.txt', email_context)
                email_body_html = render_to_string('events/email/events_registration.html', email_context)

                send_mail(
                    email_subject,
                    strip_tags(email_body_text),
                    'hopehallassembly@gmail.com',
                    ['hopehallassembly@gmail.com'],
                    html_message=email_body_html,
                    fail_silently=False,
                )

                new_registration = Registration(**cleaned_data, unique_uuid=unique_uuid)
                new_registration.save()

                return render(request, 'events/success.html')
            else:
                context.update({'goto': '#error'})

        context.update({'form': form, 'share_url': share_url, 'form_enabled': form_enabled, 'share_url_enabled': share_url_enabled})
        template_name = 'events/special-events-single.html'
    else:
        template_name = 'events/events-single.html'

    context.update({'event': occurrences[0], 'date': current_datetime.date()})
    return render(request, template_name, context)

def confirm(request, unique_uuid):
    try:
        registration = Registration.objects.get(unique_uuid=unique_uuid)
        registration.confirmed = True
        registration.save()

        if registration.event.payment_upload_needed:
            token = secrets.token_urlsafe(20)
            qr_code_token = QRCodeToken.objects.create(user=registration, token=token)

            url = f'{request.scheme}://{request.get_host()}/events/user-details/{token}/'

            qr_img = qrcode.make(url, error_correction=qrcode.constants.ERROR_CORRECT_L, border=4)
            image_stream = io.BytesIO()
            qr_img.save(image_stream, format='PNG')
            image_path = default_storage.save(f'qrcodes/{token}.png', image_stream)

            email_context = {
                'name': registration.name,
                'qr_code': default_storage.url(image_path),
                'protocol': request.scheme,
                'domain': request.get_host(),
                'event': registration.event.name,
            }

            email_subject = 'Event QR Code Generation'
            email_body_html = render_to_string('events/email/events_registration_qr.html', email_context)

            msg = EmailMessage(
                subject=email_subject,
                body=strip_tags(email_body_html),
                from_email='hopehallassembly@gmail.com',
                to=['hopehallassembly@gmail.com'],
            )
            msg.attach_alternative(email_body_html, "text/html")
            msg.send()

            return render(request, 'events/confirmed-qr.html')

        return render(request, 'events/confirmed.html')
    except Registration.DoesNotExist:
        return render(request, 'events/invalid_link.html')

@login_required
@user_passes_test(lambda user: user.is_authenticated and user.is_superuser)
def user_details(request, token):
    registration = get_object_or_404(Registration, qrcodetoken__token=token)

    if not registration.confirmed:
        return render(request, 'events/not_confirmed.html')

    return render(request, 'events/user-details.html', {'user': registration})

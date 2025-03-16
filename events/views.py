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
from hha.settings import EMAIL_HOST_USER


def home(request):
    now = timezone.now()
    two_months_later = now + timedelta(days=60)
    
    # Retrieve all events (unchanged, but you can add filtering if needed)
    events = Event.objects.all().order_by('start_time')
    
    # Build a list of upcoming occurrences using list comprehension
    upcoming_occurrences = sorted(
        [
            {'event': event, 'date': occ.date()}
            for event in events
            for occ in event.get_occurrences(now, two_months_later)
        ],
        key=lambda x: (x['date'], x['event'].start_time)
    )
    
    # Paginate the occurrences (6 per page) using get_page() to handle invalid pages gracefully
    paginator = Paginator(upcoming_occurrences, 6)
    page = request.GET.get('page', 1)
    occurrence_page = paginator.get_page(page)
    
    context = {'events': occurrence_page}
    return render(request, 'events/events.html', context)

def all_events(request):
    now = timezone.now()
    two_months_later = now + timedelta(days=60)
    six_months_ago = now - timedelta(days=180)

    # Fetch and filter events early (using the same ordering as before)
    events = Event.objects.all().order_by('start_time')

    # Build a list of occurrences for each event with complete details using list comprehension
    event_occurrences = sorted(
        [
            {'event': event, 'date': occ.date()}
            for event in events
            for occ in event.get_occurrences(six_months_ago, two_months_later)
        ],
        key=lambda x: (x['date'], x['event'].start_time)
    )

    # Paginate the occurrences (6 per page); get_page handles invalid pages gracefully
    paginator = Paginator(event_occurrences, 6)
    page = request.GET.get('page', 1)
    occurrence_page = paginator.get_page(page)

    return render(request, 'events/events-all.html', {'events': occurrence_page})

def single(request, slug, date):
    event = get_object_or_404(Event, slug=slug)
    now = timezone.now()
    two_months_later = now + timedelta(days=60)
    six_months_ago = now - timedelta(days=3600)

    # Convert the date string to a timezone-aware datetime
    date_start = datetime.combine(datetime.strptime(date, '%Y-%m-%d').date(), time.min)
    date_start = timezone.make_aware(date_start, timezone.get_current_timezone())

    # Retrieve the occurrence for this event on the target date using a list comprehension
    occurrences = [
        {'event': event, 'date': occ.date()}
        for occ in event.get_occurrences(six_months_ago, two_months_later)
        if occ.date() == date_start.date()
    ]

    share_url = request.build_absolute_uri()
    current_datetime = timezone.now()
    occ = occurrences[0]  # Assuming at least one occurrence exists
    context = {'event': occ, 'date': current_datetime.date()}

    # Determine if the form should be enabled
    if (occ['date'] < current_datetime.date() or
        (occ['date'] == current_datetime.date() and 
         occ['event'].start_time < (current_datetime + timedelta(hours=1)).time())):
        form_enabled = False
        share_url_enabled = False
    else:
        form_enabled = True
        share_url_enabled = True

    success = False  # Flag to indicate successful registration

    if occ['event'].is_special:
        if occ['event'].rsvp_form_needed:
            form_cls = NewRegistrationFormwithProof if occ['event'].payment_upload_needed else NewRegistrationForm
            form = form_cls(request.POST, request.FILES, slug=slug) if request.method == 'POST' else form_cls(slug=slug)
        else:
            form = None

        if request.method == 'POST' and form:
            if form.is_valid():
                cleaned_data = form.cleaned_data
                name = cleaned_data['name']
                # Assumes name splits into two parts (first and last)
                first_name, last_name = name.split()
                swapped_name = f"{last_name} {first_name}"
                unique_uuid = uuid.uuid4()
                # Dynamically add a hidden unique_uuid field
                form.fields['unique_uuid'] = forms.CharField(widget=forms.HiddenInput, initial=unique_uuid)

                email_context = {
                    'protocol': request.scheme,
                    'domain': request.get_host(),
                    'unique_uuid': unique_uuid,
                    **cleaned_data,
                }

                existing = Registration.objects.filter(
                    Q(name__iexact=name) | Q(name__iexact=swapped_name),
                    event=event,
                    date=occ['date']
                ).first()

                if existing:
                    form.add_error('name', f'You are already registered for {occ["event"]} {occ["date"]}.')
                    context.update({
                        'form': form,
                        'goto': '#alert',
                        'share_url': share_url,
                        'form_enabled': form_enabled,
                        'share_url_enabled': share_url_enabled
                    })
                    return render(request, 'events/special-events-single.html', context)

                email_subject = 'Event Registration'
                email_body_text = render_to_string('events/email/events_registration.txt', email_context)
                email_body_html = render_to_string('events/email/events_registration.html', email_context)

                # Uncomment and configure send_mail as needed
                send_mail(
                    email_subject,
                    strip_tags(email_body_text),
                    EMAIL_HOST_USER,
                    [EMAIL_HOST_USER],
                    html_message=email_body_html,
                    fail_silently=False,
                )

                new_registration = Registration(**cleaned_data, unique_uuid=unique_uuid, date=occ['date'])
                new_registration.save()

                success = True
                form = form_cls(slug=slug)

        context.update({
            'goto': '#alert',
            'form': form,
            'share_url': share_url,
            'form_enabled': form_enabled,
            'share_url_enabled': share_url_enabled,
            'success': success,
        })
        template_name = 'events/special-events-single.html'
    else:
        template_name = 'events/events-single.html'

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
            plain_body = strip_tags(email_body_html)

            send_mail(
                email_subject,
                plain_body,
                EMAIL_HOST_USER,
                [registration.email],
                html_message=email_body_html,
                fail_silently=False,
            )

            return render(request, 'events/confirmed-qr.html')

        return render(request, 'events/confirmed.html')
    except Registration.DoesNotExist:
        return render(request, 'events/invalid-link.html')

@login_required
@user_passes_test(lambda user: user.is_authenticated and user.is_superuser)
def user_details(request, token):
    registration = get_object_or_404(Registration, qrcodetoken__token=token)

    if not registration.confirmed:
        return render(request, 'events/not-confirmed.html')

    return render(request, 'events/user-details.html', {'user': registration})
    ## user-details.html does not exist in the repository. It should be created in the events/templates/events/ directory.

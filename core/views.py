import random
import requests
from collections import defaultdict
from datetime import timedelta, datetime
from django.shortcuts import render
from django.utils import timezone
from events.models import Event
from hha.bible import bible
from hha.votd import get_votd
from ministries.models import DepartmentLeader
from requests.exceptions import RequestException
from core.models import InspirationalQuote
from core.forms import NewContactForm

def is_internet_connected():
    try:
        response = requests.get("http://www.google.com", timeout=2)
        return True if response.status_code == 200 else False
    except RequestException:
        return False

def home(request):
    now = timezone.now()
    two_months_later = now + timedelta(days=60)
    
    # Retrieve all events (you can add filtering if needed)
    events = Event.objects.all().order_by('start_time')
    
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

    quotes = list(InspirationalQuote.objects.all().values())
    random.shuffle(quotes)
    random_quote = random.choice(quotes)

    reference, passage, version = '', '', ''
    if is_internet_connected():
        votd_data = get_votd()
        if votd_data:
            reference, passage, version = votd_data['verse']['details']['reference'], votd_data['verse']['details']['text'], votd_data['verse']['details']['version']

    context = {
        'events1': upcoming_occurrences[:3],
        'events2': upcoming_occurrences[:6],
        'quote': random_quote,
        'reference': reference,
        'passage': passage,
        'version': version,
    }
    return render(request, 'core/index.html', context)

def about(request):
    leader_roles = defaultdict(list)

    leadership = DepartmentLeader.objects.select_related('leader__worker')
    for leader in leadership:
        leader_roles[leader.leader.worker.name].append(leader.department.name)

    formatted_data = []
    for leader_name, roles in leader_roles.items():
        num_roles = len(roles)
        if num_roles > 1:
            formatted_roles = ', '.join(roles[:-1]) + f' & {roles[-1]}'
        else:
            formatted_roles = roles[0]

        formatted_data.append({
            'name': leader_name,
            'roles': formatted_roles,
            'image': leadership.filter(leader__worker__name=leader_name).first().leader.image,
        })

    if is_internet_connected():
        bible_verse = bible('john 3:16-17', 'esv')
        reference, passage, version = bible_verse['reference'], bible_verse['text'], bible_verse['translation_id']
    else:
        reference, passage, version = '', '', ''

    context = {
        'leadership': formatted_data,
        'reference': reference,
        'passage': passage,
        'version': version,
    }
    return render(request, 'core/about.html', context)

def contact(request):
    context = {}
    if request.method == 'POST':
        form = NewContactForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            name = cleaned_data['name']
            phone_number = cleaned_data['phone_number']
            email = cleaned_data['email']
            message = cleaned_data['message']

            pass

        else:
            context.update({'form': form, 'goto': '#error'})

    else:
        form = NewContactForm()
        
    context.update({'form': form})

    return render(request, 'core/contact.html', context)

def giving(request):
    return render(request, 'core/giving.html')

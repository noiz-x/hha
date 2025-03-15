import uuid
from core.models import Worker
from django import forms
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ministries.forms import NewWorkerForm
from ministries.models import Department, DepartmentWorker
from hha.settings import EMAIL_HOST_USER


def home(request):
    context = {}
    departments = Department.objects.filter()

    if request.method == 'POST':
        form = NewWorkerForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            name = cleaned_data['name']
            phone_number = cleaned_data['phone_number']
            email = cleaned_data['email']
            department = cleaned_data['department'].name
            question = cleaned_data['question']
            comment = cleaned_data['comment']

            unique_uuid = uuid.uuid4()
            form.fields['unique_uuid'] = forms.CharField(widget=forms.HiddenInput, initial=unique_uuid)

            email_context = {
                'protocol': request.scheme,
                'domain': request.get_host(),
                'name': name,
                'phone_number': phone_number,
                'email': email,
                'department': department,
                'question': question,
                'comment': comment,
                'unique_uuid': unique_uuid,
            }

            email_subject = 'New Worker Registration'
            email_body_text = render_to_string('ministries/email/confirm_notification.txt', email_context)
            email_body_html = render_to_string('ministries/email/confirm_notification.html', email_context)

            existing_worker = Worker.objects.filter(
                Q(name__iexact=name) |
                Q(name__iexact=swapped_name)
            ).first()

            if existing_worker:
                form.add_error('name', 'Worker already exists.')
                return render(request, 'ministries/volunteer.html', {'departments': departments, 'form': form, 'goto': '#alert'})

            # send_mail(
            #     email_subject,
            #     strip_tags(email_body_text),
            #     EMAIL_HOST_USER,
            #     [EMAIL_HOST_USER],
            #     html_message=email_body_html,
            #     fail_silently=False,
            # )
            print(strip_tags(email_body_text))

            # new_worker = Worker.objects.create(
            #     name=name,
            #     phone_number=phone_number,
            #     email=email,
            #     department=department,
            #     unique_uuid=unique_uuid,
            # )
            # new_worker.save()

        context.update({'departments': departments, 'form': form, 'goto': '#alert'})
    else:
        form = NewWorkerForm()

    context.update({
        'departments': departments,
        'form': form
    })
    return render(request, 'ministries/volunteer.html', context)


def confirm(request, unique_uuid):
    try:
        worker = Worker.objects.get(unique_uuid=unique_uuid)
        worker.confirmed = True
        worker.save()
        new_worker_dept = DepartmentWorker.objects.create(worker=worker, department__name=worker.department)
        new_worker_dept.save()
        return render(request, 'ministries/confirmed.html')
    except Worker.DoesNotExist:
        return render(request, 'ministries/invalid_link.html')

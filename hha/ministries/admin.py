from django.contrib import admin
from ministries.models import Department, DepartmentLeader, DepartmentWorker

admin.site.register(Department)
admin.site.register(DepartmentWorker)
admin.site.register(DepartmentLeader)

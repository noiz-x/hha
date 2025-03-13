from django.db import models
from core.models import Leader, Worker

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DepartmentLeader(models.Model):
    leader = models.ForeignKey(Leader, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['leader', 'department']

    def __str__(self):
        return f"{self.leader.worker.name} - {self.department.name}"

class DepartmentWorker(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, swappable=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['worker', 'department']

    def __str__(self):
        return f"{self.worker.name} - {self.department.name}"


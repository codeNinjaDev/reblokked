from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields import BooleanField

from datetime import date
# Create your models here.
class User(AbstractUser):
    pass

class TaskList(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    bookmarked = BooleanField(db_index=True, default=False)
    default_list = BooleanField(default=True)
    date_created = models.DateField(db_index=True, default=date.today)
    list_name = models.CharField(max_length=25, default=date.today)

    def __str__(self) -> str:
        return f"{self.list_name}"

class Task(models.Model):
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=25)
    completed = models.BooleanField(default=False)
    start_time = models.TimeField() # start time of task
    task_length = models.IntegerField() # how many minutes task will take

    def __str__(self) -> str:
        return f"{'✅' if self.completed else '❌'} {self.task_name} on {self.task_list} starting at {self.start_time}"

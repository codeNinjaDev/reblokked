from rest_framework import serializers
from .models import TaskList, Task

class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskList
        exclude = ['creator']
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ['task_list']
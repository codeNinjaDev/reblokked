# auth0authorization/urls.py

from django.urls import path

from . import views

urlpatterns = [
    path('api/task-list', views.task_list),
    path('api/task', views.task),
    path('api/user', views.get_username),
]

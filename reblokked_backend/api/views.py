from datetime import date, datetime
from django.shortcuts import render

# Create your views here.
# auth0authorization/views.py

from functools import wraps
import jwt

from django.http import JsonResponse

from .models import User, TaskList, Task
from .utils import jwt_decode_token, jwt_get_username_from_payload_handler

from .serializers import TaskListSerializer, TaskSerializer

def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token

def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope


from django.http import JsonResponse
from rest_framework.decorators import api_view



@api_view(['GET'])
def get_username(request):
    token = request.auth
    payload = jwt_decode_token(token)
    username = jwt_get_username_from_payload_handler(payload)

    user = User.objects.filter(username=username)
    print(user)
    return JsonResponse({'message': username})

@api_view(['GET', 'POST'])
def task_list(request):

    if request.method == "POST":
        t = TaskListSerializer(data=request.data) 
        if t.is_valid():
            # delete duplicates
            if "date_created" in request.data:
                date_created = datetime.strptime(request.data["date_created"], "%Y-%m-%d")
            else:
                date_created = date.today()
            # remove duplicates
            TaskList.objects.filter(date_created=date_created, bookmarked=False).all().delete()
            t.save(creator=request.user)
            return JsonResponse(t.data)
        else:
            response = JsonResponse({"message": "Malformed json"})
            response.status_code = 400
            return response
    selected_lists = TaskList.objects.filter(creator=request.user)

    date_filter = request.query_params.get('date-created')
    bookmark_filter = request.query_params.get('bookmarked')

    if date_filter is not None:
        date_created = datetime.strptime(date_filter, "%Y-%m-%d")
        selected_lists = selected_lists.filter(date_created=date_created)
    if bookmark_filter is not None:
        selected_lists = selected_lists.filter(bookmarked=bookmark_filter)

    serializer = TaskListSerializer(selected_lists, many=True)
    return JsonResponse({'lists': serializer.data})

@api_view(['GET', 'POST'])
def task(request):
    
    task_list_id = request.query_params.get('task-list-id')
    if not task_list_id:
        response = JsonResponse({"message": "Must include Task List id"})
        response.status_code = 400
        return response
    task_list = TaskList.objects.filter(id=task_list_id).first()
    if request.method == "POST":
        t = TaskSerializer(data=request.data) 
        if t.is_valid():
            t.save(task_list=task_list)
            return JsonResponse(t.data)
        else:
            response = JsonResponse({"message": "Malformed json"})
            response.status_code = 400
            return response
    serializer = TaskSerializer(Task.objects.filter(task_list=task_list), many=True)
    return JsonResponse({'tasks': serializer.data})

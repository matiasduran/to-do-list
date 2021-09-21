from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Task
from .forms import TaskForm, StatusTaskForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
import datetime

@login_required
def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    # task_list = Task.objects.order_by('id')
    # exclude archived tasks
    task_list = Task.objects\
        .filter(author=request.user)\
        .exclude(status="a")\
        .exclude(status="b")\
        .order_by('priority')

    task_list_backlog = Task.objects\
        .filter(author=request.user)\
        .filter(status='b')\
        .order_by('priority')

    task_form = TaskForm(initial={'priority': '2'})

    context = {
        'task_list': task_list,
        'task_list_backlog': task_list_backlog,
        'task_form': task_form,
    }
    return render(request, 'task_app/index.html', context)
"""
@login_required
def create_task(request):
    new_task = None

    if request.method == 'POST':
        # A comment was posted
        new_task = Task.objects.create(
            description=description_data,
        )
        # Create task object but don't save to database yet
        new_task = task_form.save(commit=False)
        # Save the task to the database
        new_task.status = 'wip'
        new_task.save()
        return redirect('task_app:index')
    else:
        task_form = TaskForm()

    context = {
        #'post': post,
        #'comments': comments,
        'new_task': new_task,
        'task_form': task_form
    }

    return render(
        request,
        'task_app/create.html',
        context
    )
"""


@login_required
def edit_status_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.author == request.user:
        if task.status == 'b':
            task.status = 'wip'
            task.last_working_time = timezone.now()
        elif task.status == 'wip':
            working_time = task.spent_time + (timezone.now() - task.last_working_time)
            # round working time deleting microseconds
            task.spent_time = working_time - datetime.timedelta(microseconds=working_time.microseconds)
            task.status = 'd'
        elif task.status == 'd':
            task.status = 'b'
        elif task.status == 'a':
            task.status = 'b'
            task.save()
            return redirect('task_app:show_all_archived')
        
        task.save()
        return redirect('task_app:index')
    else:
        return HttpResponse('Unauthorized', status=401)

@login_required
def create_task(request):

    new_task = None

    if request.method == 'POST':
        # A comment was posted
        task_form = TaskForm(data=request.POST)
        if task_form.is_valid():
            # Create task object but don't save to database yet
            new_task = task_form.save(commit=False)
            # Save the task to the database
            new_task.status = 'b'
            new_task.author = request.user
            new_task.save()
            return redirect('task_app:index')
    else:
        task_form = TaskForm()

    context = {
        #'post': post,
        #'comments': comments,
        'new_task': new_task,
        'task_form': task_form
    }

    return render(
        request,
        'task_app/create.html',
        context
    )

@login_required
def archive_all_tasks(request):
    task_list = Task.objects\
        .filter(author=request.user)\
        .filter(status='d')
    for task in task_list:
        task.status = 'a'
        task.save()
    return redirect('task_app:index')

@login_required
def delete_archived_tasks(request):
    task_list = Task.objects\
        .filter(author=request.user)\
        .filter(status='a')
    for task in task_list:
        task.status = 'a'
        task.delete()
    return redirect('task_app:show_all_archived')

@login_required
def send_backlog_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # check if user is allowed to edit tasks
    if task.author == request.user:
        # check if task must be edited
        if task.status not in ('b', 'bb'):
            return HttpResponse('Method not allowed', status=405)
        if task.status == 'bb':
            task.status = 'b'
        elif task.status == 'b':
            task.status = 'bb'
        task.save()
        return redirect('task_app:show_bottom_backlog')
    else:
        return HttpResponse('Unauthorized', status=401)

@login_required
def show_all_archived(request):
    task_list = Task.objects\
        .filter(author=request.user)\
        .filter(status='a')\
        .order_by('priority')
    
    context = {'task_list': task_list}
    return render(request, 'task_app/index.html', context)

@login_required
def show_bottom_backlog(request):
    task_list_bottom_backlog = Task.objects\
        .filter(author=request.user)\
        .filter(status='bb')\
        .order_by('priority')
    task_list_backlog = Task.objects\
        .filter(author=request.user)\
        .filter(status='b')\
        .order_by('priority')

    # paginate archived tasks
    page = request.GET.get('page', 1)
    paginator = Paginator(task_list_bottom_backlog, 7)
    try:
        bottom_backlog_tasks = paginator.page(page)
    except PageNotAnInteger:
        bottom_backlog_tasks = paginator.page(1)
    except EmptyPage:
        bottom_backlog_tasks = paginator.page(paginator.num_pages)

    context = {
        'task_list_backlog': task_list_backlog,
        'task_list_bottom_backlog': bottom_backlog_tasks,
    }
    return render(request, 'task_app/list_backlog.html', context)
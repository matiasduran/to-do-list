from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Task, Tag
from .forms import TaskForm, StatusTaskForm, TagForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.core import serializers
import datetime
import json

@login_required
def index(request):
    tag = Tag.objects.get_or_create(name='all', author=request.user)[0]
    tag_id = tag.pk
    return redirect('task_app:index_tag', tag_id=tag_id)


@login_required
def index_tag(request, tag_id):
    
    if tag_id is None:
        tag = Tag.objects.get_or_create(name='all', author=request.user)[0]
        tag_id = tag.pk
    else:
        tag = get_object_or_404(Tag, id=tag_id)

    # exclude archived tasks
    task_list = Task.objects\
        .filter(author=request.user)\
        .filter(tag=tag_id)\
        .exclude(status="a")\
        .exclude(status="b")\
        .order_by('priority')

    task_list_backlog = Task.objects\
        .filter(author=request.user)\
        .filter(tag=tag_id)\
        .filter(status='b')\
        .order_by('priority')

    task_form = TaskForm(initial={'priority': '2'})

    tag_list = Tag.objects.filter(author=request.user)

    context = {
        'task_list': task_list,
        'task_list_backlog': task_list_backlog,
        'task_form': task_form,
        'tag_list': tag_list,
        'selected_tag': tag
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
def edit_status_task(request, tag_id, task_id):
    task = get_object_or_404(Task, id=task_id)

    if tag_id is None:
        tag = Tag.objects.get_or_create(name='all', author=request.user)[0]
        tag_id = tag.pk

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
            return redirect('task_app:show_all_archived', tag_id=tag_id)
        
        task.save()
        return redirect('task_app:index_tag', tag_id=tag_id)
    else:
        return HttpResponse('Unauthorized', status=401)

@login_required
def create_task(request, tag_id):

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
            tag_all = Tag.objects.get_or_create(name='all', author=request.user)[0]
            if Tag.objects.filter(pk=tag_id).exists():
                tag = (get_object_or_404(Tag, pk=tag_id))
                new_task.tag.add(tag, tag_all)
            else:
                new_task.tag.add(tag_all)

            new_task.save()
            return redirect('task_app:index_tag', tag_id=tag_id)
    else:
        task_form = TaskForm()

    tag = get_object_or_404(Tag, id=tag_id)
    context = {
        #'post': post,
        #'comments': comments,
        'new_task': new_task,
        'task_form': task_form,
        'selected_tag': tag
    }

    return render(
        request,
        'task_app/create.html',
        context
    )

@login_required
def archive_all_tasks(request, tag_id):

    if tag_id is None:
        tag = Tag.objects.get_or_create(name='all', author=request.user)[0]
        tag_id = tag.pk

    task_list = Task.objects\
        .filter(author=request.user)\
        .filter(tag=tag_id)\
        .filter(status='d')
    for task in task_list:
        task.status = 'a'
        task.save()
    
    return redirect('task_app:index_tag', tag_id=tag_id)

@login_required
def delete_archived_tasks(request, tag_id):

    if tag_id is None:
        tag = Tag.objects.get_or_create(name='all', author=request.user)[0]
        tag_id = tag.pk

    task_list = Task.objects\
        .filter(author=request.user)\
        .filter(tag=tag_id)\
        .filter(status='a')
    for task in task_list:
        task.status = 'a'
        task.delete()
    return redirect('task_app:show_all_archived', tag_id=tag_id)

@login_required
def send_backlog_task(request, tag_id, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if tag_id is None:
        tag = Tag.objects.get_or_create(name='all', author=request.user)[0]
        tag_id = tag.pk

    tag_list = Tag.objects.filter(author=request.user)

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
        return redirect('task_app:show_bottom_backlog', tag_id=tag_id)
    else:
        return HttpResponse('Unauthorized', status=401)

@login_required
def show_all_archived(request, tag_id):

    if tag_id is None:
        tag = Tag.objects.get_or_create(name='all', author=request.user)[0]
        tag_id = tag.pk
    else:
        tag = get_object_or_404(Tag, id=tag_id)

    tag_list = Tag.objects.filter(author=request.user)

    task_list = Task.objects\
        .filter(author=request.user)\
        .filter(tag=tag_id)\
        .filter(status='a')\
        .order_by('priority')

    context = {
        'task_list': task_list,
        'tag_list': tag_list,
        'selected_tag': tag
    }
    return render(request, 'task_app/show_all_archived.html', context)

@login_required
def show_bottom_backlog(request, tag_id):

    if tag_id is None:
        tag = Tag.objects.get_or_create(name='all', author=request.user)[0]
        tag_id = tag.pk
    else:
        tag = get_object_or_404(Tag, id=tag_id)

    tag_list = Tag.objects.filter(author=request.user)

    task_list_bottom_backlog = Task.objects\
        .filter(author=request.user)\
        .filter(tag=tag_id)\
        .filter(status='bb')\
        .order_by('priority')
    task_list_backlog = Task.objects\
        .filter(author=request.user)\
        .filter(tag=tag_id)\
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
        'tag_list': tag_list,
        'selected_tag': tag
    }
    return render(request, 'task_app/list_backlog.html', context)

@login_required
def download_backup(request):
    task_list = Task.objects.filter(author=request.user)

    field_list = (
        'description',
        'priority',
        'status',
        #'author',
        #'last_working_time',
        'spent_time',
        'tag',
    )

    # convert model to text with list of dicts
    task_list_json = serializers.serialize('json', task_list, fields=field_list)

    # extract just fields of dict
    task_list_json = [task['fields'] for task in json.loads(task_list_json)]

    response = HttpResponse(
        json.dumps(task_list_json),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment;'\
        'filename="task_list_{user}_{date_year}{date_month:02d}{date_day:02d}.json"'.format(
        user=request.user,
        date_year=timezone.now().year,
        date_month=timezone.now().month,
        date_day=timezone.now().day
    )

    return response

@login_required
def create_tag(request, tag_id):

    new_tag = None

    if request.method == 'POST':
        tag_form = TagForm(data=request.POST)
        if tag_form.is_valid():
            # Create tag object but don't save to database yet
            new_tag = tag_form.save(commit=False)
            # Save the tag to the database
            new_tag.author = request.user
            new_tag.save()
            return redirect('task_app:index_tag', tag_id=new_tag.pk)
    else:
        tag_form = TagForm()

    tag = get_object_or_404(Tag, id=tag_id)
    context = {
        'new_tag': new_tag,
        'tag_form': tag_form,
        'selected_tag': tag
    }

    return render(
        request,
        'task_app/create_tag.html',
        context
    )

# remove tag
# edit (or add) tag
def import_tasks(request, tag_id):
    # source code based in: https://pythoncircle.com/post/30/how-to-upload-and-process-the-csv-file-in-django/

    if request.method == 'POST':
        batch_file = request.FILES["batch_file"]

        if not batch_file.name.endswith('.json'):
            return HttpResponse('Internal Server Error', status=500)
            # messages.error(request,'File is not JSON type')
            # return redirect("task_app:import_tasks")
        #if file is too large, return
        if batch_file.multiple_chunks():
            return HttpResponse('Internal Server Error', status=500)
            # messages.error(request,"Uploaded file is too big (%.2f MB)." % (batch_file.size/(1000*1000),))
            # return redirect("task_app:import_tasks")

        file_data = batch_file.read().decode("utf-8")
        file_data_list = json.loads(file_data)

        for task in file_data_list:
            try:
                new_task = Task.objects.create(
                    description=task['description'],
                    priority=task['priority'],
                    status=task['status'],
                )
                new_task.spent_time = datetime.timedelta(
                    hours=int(task['spent_time'].split(':')[0]),
                    minutes=int(task['spent_time'].split(':')[1]),
                )

                new_task.author = request.user
                new_task.last_working_time = timezone.now()
                
                new_task.save()

                # add tag to tasks
                tag_all = Tag.objects.get_or_create(name='all', author=request.user)[0]

                if 'tag' in task.keys():
                    for tag_id in task['tag']:
                        if Tag.objects.filter(pk=tag_id).exists():
                            tag = (get_object_or_404(Tag, pk=tag_id))
                            new_task.tag.add(tag, tag_all)
                        else:
                            new_task.tag.add(tag_all)
                else:
                    new_task.tag.add(tag_all)
                    
                new_task.save()

            except:
                return HttpResponse('Internal Server Error', status=500)
        tag = get_object_or_404(Tag, id=tag_id)
        context = {'success': True, 'selected_tag': tag}
        return render(request, "task_app/import_tasks.html", context)

    elif "GET" == request.method:
        tag = get_object_or_404(Tag, id=tag_id)
        return render(request, "task_app/import_tasks.html", {'selected_tag': tag})

    return redirect("task_app:import_tasks", tag_id=tag_d)

@login_required
def block_task(request, tag_id, task_id):
    task = get_object_or_404(Task, id=task_id)

    if tag_id is None:
        tag = Tag.objects.get_or_create(name='all', author=request.user)[0]
        tag_id = tag.pk

    if task.author == request.user:
        task.status = 'b'
        if not task.is_blocked:
            task.is_blocked = True
        else:
            task.is_blocked = False
        
        task.save()
        return redirect('task_app:index_tag', tag_id=tag_id)
    else:
        return HttpResponse('Unauthorized', status=401)
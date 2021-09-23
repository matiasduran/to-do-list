from django.urls import path

from . import views

app_name = 'task_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('task/create/', views.create_task, name='create_task'),
    path('task/<int:task_id>/edit_status/', views.edit_status_task, name='edit_status_task'),
    path('task/<int:task_id>/send_backlog/', views.send_backlog_task, name='send_backlog_task'),
    path('task/archive_all/', views.archive_all_tasks, name='archive_all_tasks'),
    path('show_all_archived/', views.show_all_archived, name='show_all_archived'),
    path('show_bottom_backlog/', views.show_bottom_backlog, name='show_bottom_backlog'),
    path('task/delete_archived_tasks/', views.delete_archived_tasks, name='delete_archived_tasks'),
    path('task/download_backup/', views.download_backup, name='download_backup'),
    path('create_tag/', views.create_tag, name='create_tag'),
]
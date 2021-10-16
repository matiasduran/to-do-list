from django.urls import path

from . import views

app_name = 'task_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('tag/<int:tag_id>/task/create/', views.create_task, name='create_task'),
    path('tag/<int:tag_id>/task/<int:task_id>/edit_status/', views.edit_status_task, name='edit_status_task'),
    path('tag/<int:tag_id>/task/<int:task_id>/send_backlog/', views.send_backlog_task, name='send_backlog_task'),
    path('tag/<int:tag_id>/task/<int:task_id>/block/', views.block_task, name='block_task'),
    path('tag/<int:tag_id>/task/archive_all/', views.archive_all_tasks, name='archive_all_tasks'),
    path('tag/<int:tag_id>/show_all_archived/', views.show_all_archived, name='show_all_archived'),
    path('tag/<int:tag_id>/show_bottom_backlog/', views.show_bottom_backlog, name='show_bottom_backlog'),
    path('tag/<int:tag_id>/task/delete_archived_tasks/', views.delete_archived_tasks, name='delete_archived_tasks'),
    path('task/download_backup/', views.download_backup, name='download_backup'),
    path('tag/<int:tag_id>/create_tag/', views.create_tag, name='create_tag'),
    path('tag/<int:tag_id>/task/import_tasks/', views.import_tasks, name='import_tasks'),
    path('tag/<int:tag_id>/', views.index_tag, name='index_tag'),
]
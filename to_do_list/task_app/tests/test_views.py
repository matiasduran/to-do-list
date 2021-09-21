from django.test import TestCase
from django.urls import reverse
from task_app.models import Task, User
from django.shortcuts import get_object_or_404
import datetime

"""
List of Views:
- index
- create_task
- edit_status_task
- create_task
- archive_all_tasks
- delete_archived_tasks
+ send_backlog_task
+ show_all_archived
- show_bottom_backlog

Features:
- index
    - show list of tasks WIP, backlog and done.
- create_task
    - create a new task, only for the user.
- edit_status_task
    - edit status of the tasks.
- archive_all_tasks
    - it changes all backlog tasks to archived.
- delete_archived_tasks
    - it deleted all archived tasks.
- send_backlog_task
- show_all_archived
- show_bottom_backlog

"""

class ShowAllArchivedViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create 13 users
        number_of_users = 13
        for user_num in range(number_of_users):
            user = User.objects.create_user(
                username=f'Matias {user_num}',
                password='123456'
            )

            # create 10 tasks in backlog per user
            number_of_tasks = 10
            for task_num in range(number_of_tasks):
                Task.objects.create(
                    description='This is a little task \# {task_num}',
                    priority='1',
                    status='b',
                    author=user,
                    # last_working_time=,
                    spent_time=datetime.timedelta(seconds=15),
                )

            # create 8 archived tasks per user
            number_of_tasks = 8
            for task_num in range(number_of_tasks):
                Task.objects.create(
                    description='This is a little archived task \# {task_num}',
                    priority='1',
                    status='a',
                    author=user,
                    # last_working_time=,
                    spent_time=datetime.timedelta(seconds=15),
                )


    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('task_app:show_all_archived'))
        self.assertRedirects(resp, '/accounts/login/?next=/show_all_archived/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='Matias 1', password='123456')
        resp = self.client.get(reverse('task_app:show_all_archived'))

        #Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'Matias 1')
        #Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)
        #Check we used correct template
        self.assertTemplateUsed(resp, 'task_app/index.html')

    def test_list_all_archived_tasks(self):
        login = self.client.login(username='Matias 1', password='123456')
        resp = self.client.get(reverse('task_app:show_all_archived'))

        #Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'Matias 1')
        #Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)
        
        self.assertTrue('task_list' in resp.context)
        
        # Check if all tasks are archived
        for task in resp.context['task_list']:
            self.assertEqual(task.status, 'a')
        
        #Check if there are all the requested tasks
        self.assertEqual( len(resp.context['task_list']), 8)

class SendBacklogTaskViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create users
        number_of_users = 2
        for user_num in range(number_of_users):
            user = User.objects.create_user(
                username=f'Matias {user_num}',
                password='123456'
            )

            # create 10 tasks in backlog per user
            number_of_tasks = 10
            for task_num in range(number_of_tasks):
                Task.objects.create(
                    description=f'This is a little task \# {task_num}',
                    priority='1',
                    status='b',
                    author=user,
                    # last_working_time=,
                    spent_time=datetime.timedelta(seconds=15),
                )

            # create 8 archived tasks per user
            number_of_tasks = 8
            for task_num in range(number_of_tasks):
                Task.objects.create(
                    description=f'This is a little archived task \# {task_num} by {user_num}',
                    priority='1',
                    status='a',
                    author=user,
                    # last_working_time=,
                    spent_time=datetime.timedelta(seconds=15),
                )

            # create 5 bottom backlog tasks per user
            number_of_tasks = 5
            for task_num in range(number_of_tasks):
                Task.objects.create(
                    description=f'This is a little archived task \# {task_num} by {user_num}',
                    priority='1',
                    status='bb',
                    author=user,
                    # last_working_time=,
                    spent_time=datetime.timedelta(seconds=15),
                )

    def test_redirect_if_not_logged_in_with_template(self):
        ID_TASK = 5
        resp = self.client.get(reverse('task_app:send_backlog_task', kwargs={'task_id': ID_TASK}))
        self.assertRedirects(resp, f'/accounts/login/?next=/task/{ID_TASK}/send_backlog/')

    def test_redirect_if_not_logged_in_with_url(self):
        ID_TASK = 5
        RIGHT_URL = f'/task/{ID_TASK}/send_backlog/'
        resp = self.client.get(RIGHT_URL)
        self.assertRedirects(resp, f'/accounts/login/?next={RIGHT_URL}')

    def test_logged_in_redirects_backlog_page(self):

        USER = 'Matias 1'

        # Login user
        user = User.objects.filter(username=USER)[0]
        login = self.client.force_login(user)
        resp = self.client.get(reverse('task_app:index'))

        # get a task of this user
        id_task = Task.objects.filter(author=user)[0].id
        
        # check if ir redirects right
        resp = self.client.get(reverse('task_app:send_backlog_task', kwargs={'task_id': id_task}))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('task_app:show_bottom_backlog'))

    def test_logged_in_sends_tasks_to_backlog(self):

        USER = 'Matias 1'
        
        # login user
        user = User.objects.filter(username=USER)[0]
        login = self.client.force_login(user)        
        resp = self.client.get(reverse('task_app:index'))

        # get tasks at bottom backlog and converts it to backlog
        backlog_task_list = Task.objects.filter(status='bb').filter(author=user)
        for task in backlog_task_list:
            resp = self.client.get(reverse('task_app:send_backlog_task', kwargs={'task_id': task.id}))
            task = get_object_or_404(Task, id=task.id)
            self.assertEqual(task.status, 'b')

    def test_logged_in_sends_tasks_to_bottom_backlog(self):
        
        USER = 'Matias 1'

        # login user
        user = User.objects.filter(username=USER)[0]
        login = self.client.force_login(user)
        resp = self.client.get(reverse('task_app:index'))

        # get tasks at backlog and converts it to bottom backlog
        backlog_task_list = Task.objects.filter(status='b').filter(author=user)
        for task in backlog_task_list:
            resp = self.client.get(reverse('task_app:send_backlog_task', kwargs={'task_id': task.id}))
            task = get_object_or_404(Task, id=task.id)
            self.assertEqual(task.status, 'bb')

    def test_logged_in_doesnt_change_active_tasks(self):
        USER = 'Matias 1'

        # login user
        user = User.objects.filter(username=USER)[0]
        login = self.client.force_login(user)
        resp = self.client.get(reverse('task_app:index'))

        # get tasks that must no editable
        backlog_task_list = Task.objects\
            .filter(author=user)\
            .exclude(status='b')\
            .exclude(status='bb')

        for task in backlog_task_list:
            old_task_status = task.status
            resp = self.client.get(reverse('task_app:send_backlog_task', kwargs={'task_id': task.id}))
            task = get_object_or_404(Task, id=task.id)
            self.assertEqual(task.status, old_task_status)
            self.assertEqual(resp.status_code, 405)

    def test_logged_in_sends_another_user_task_to_backlog(self):
        USER = 'Matias 1'

        # login user        
        user = User.objects.filter(username=USER)[0]
        login = self.client.force_login(user)
        resp = self.client.get(reverse('task_app:index'))

        backlog_task_list = Task.objects.exclude(author=user)

        for task in backlog_task_list:
            old_task_status = task.status
            resp = self.client.get(reverse('task_app:send_backlog_task', kwargs={'task_id': task.id}))
            self.assertEqual(task.status, old_task_status)
            task = get_object_or_404(Task, id=task.id)
            self.assertEqual(task.status, old_task_status)
            self.assertEqual(resp.status_code, 401)
    

    """

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        #Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 3)
    """

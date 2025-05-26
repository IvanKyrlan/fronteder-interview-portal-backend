from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('tests/<int:test_id>/tasks/', views.InteractiveTaskListView.as_view(), name='interactive_task_list'),
    path('tasks/<int:pk>/', views.InteractiveTaskDetailView.as_view(), name='interactive_task_detail'),
    path('tasks/submit/', views.SubmitTaskView.as_view(), name='submit_task'),
    path('user/task-attempts/<int:test_id>/', views.TaskAttemptListView.as_view(), name='task_attempts'),
    path('user/task-attempts/task/<int:task_id>/', views.TaskAttemptListView.as_view(), name='task_attempts_by_task'),
    path('user/task-progress/', views.UserTaskProgressListView.as_view(), name='user_task_progress'),
    path('user/task-progress/<int:test_id>/', views.UserTaskProgressDetailView.as_view(), name='user_task_progress_detail'),
]
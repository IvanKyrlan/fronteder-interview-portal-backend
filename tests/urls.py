from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    path('tests/', views.TestListView.as_view(), name='test_list'),
    path('tests/<int:pk>/', views.TestDetailView.as_view(), name='test_detail'),
    path('user/progress/', views.UserProgressListCreateView.as_view(), name='user_progress'),
    path('user/progress/<int:test_id>/', views.UserProgressDetailView.as_view(), name='user_progress_detail'),
    path('user/test-attempts/<int:test_id>/', views.TestAttemptListView.as_view(), name='test_attempts'),
]
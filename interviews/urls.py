from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    path('interviews/', views.InterviewVideoListView.as_view(), name='interview-list'),
    path('interviews/<int:pk>/', views.InterviewVideoDetailView.as_view(), name='interview-detail'),
]
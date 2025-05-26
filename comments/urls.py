from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('comments/', views.CommentListView.as_view(), name='comment-list'),
    path('comments/create/', views.CommentCreateView.as_view(), name='comment-create'),
]
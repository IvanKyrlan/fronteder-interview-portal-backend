# # core/urls.py
#
# from django.urls import path, re_path
# from rest_framework_simplejwt.views import TokenRefreshView
# from . import views
# from .views import CommentListView, CommentCreateView, InterviewVideoListView, InterviewVideoDetailView, ForumTopicListView, ForumTopicLikeView, ForumTopicDetailView
#
# app_name = 'core'
#
# urlpatterns = [
#     path('auth/register/', views.RegisterView.as_view(), name='register'),
#     path('auth/login/', views.LoginView.as_view(), name='login'),
#     path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#
#     path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
#     path('user/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
#
#     path('user/progress/', views.UserProgressListCreateView.as_view(), name='user_progress'),
#     path('user/progress/<int:test_id>/', views.UserProgressDetailView.as_view(), name='user_progress_detail'),
#     path('user/test-attempts/<int:test_id>/', views.TestAttemptListView.as_view(), name='test_attempts'),
#
#     path('tests/', views.TestListView.as_view(), name='test_list'),
#     path('tests/<int:pk>/', views.TestDetailView.as_view(), name='test_detail'),
#     path('tests/<int:test_id>/tasks/', views.InteractiveTaskListView.as_view(), name='interactive_task_list'),
#     path('tasks/<int:pk>/', views.InteractiveTaskDetailView.as_view(), name='interactive_task_detail'),
#     path('tasks/submit/', views.SubmitTaskView.as_view(), name='submit_task'),
#
#     path('user/task-attempts/<int:test_id>/', views.TaskAttemptListView.as_view(), name='task_attempts'),
#     path('user/task-attempts/task/<int:task_id>/', views.TaskAttemptListView.as_view(), name='task_attempts_by_task'),
#     path('user/task-progress/', views.UserTaskProgressListView.as_view(), name='user_task_progress'),
#     path('user/task-progress/<int:test_id>/', views.UserTaskProgressDetailView.as_view(),
#          name='user_task_progress_detail'),
#
#     path('articles/', views.ArticleListView.as_view(), name='article_list'),
#     path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
#
#     path('api/comments/', CommentListView.as_view(), name='comment-list'),
#     path('api/comments/create/', CommentCreateView.as_view(), name='comment-create'),
#
#     path('api/interviews/', InterviewVideoListView.as_view(), name='interview-list'),
#     path('api/interviews/<int:pk>/', InterviewVideoDetailView.as_view(), name='interview-detail'),
#
#
#     path('forum/topics/', views.ForumTopicListView.as_view(), name='forum_topic_list'),
#     path('forum/topics/<int:pk>/', views.ForumTopicDetailView.as_view(), name='forum_topic_detail'),
#     path('forum/categories/', views.ForumCategoryListView.as_view(), name='forum_category_list'),
#     path('forum/topics/<int:pk>/like/', views.ForumTopicLikeView.as_view(), name='forum_topic_like'),
#     path('forum/topics/<int:pk>/unlike/', views.ForumTopicUnlikeView.as_view(), name='forum_topic_unlike'),
#     path('forum/topics/<int:pk>/bookmark/', views.ForumTopicBookmarkView.as_view(), name='forum_topic_bookmark'),
#     path('forum/topics/<int:pk>/unbookmark/', views.ForumTopicUnbookmarkView.as_view(), name='forum_topic_unbookmark'),
#     path('forum/user/bookmarks/', views.UserBookmarksView.as_view(), name='user_bookmarks'),
#
#
#     re_path(r'^.*', views.cors_preflight),
# ]
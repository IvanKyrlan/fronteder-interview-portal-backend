from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('forum/topics/', views.ForumTopicListView.as_view(), name='forum_topic_list'),
    path('forum/topics/<int:pk>/', views.ForumTopicDetailView.as_view(), name='forum_topic_detail'),
    path('forum/categories/', views.ForumCategoryListView.as_view(), name='forum_category_list'),
    path('forum/topics/<int:pk>/like/', views.ForumTopicLikeView.as_view(), name='forum_topic_like'),
    path('forum/topics/<int:pk>/unlike/', views.ForumTopicUnlikeView.as_view(), name='forum_topic_unlike'),
    path('forum/topics/<int:pk>/bookmark/', views.ForumTopicBookmarkView.as_view(), name='forum_topic_bookmark'),
    path('forum/topics/<int:pk>/unbookmark/', views.ForumTopicUnbookmarkView.as_view(), name='forum_topic_unbookmark'),
    path('forum/user/bookmarks/', views.UserBookmarksView.as_view(), name='user_bookmarks'),
]
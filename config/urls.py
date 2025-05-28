from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('tests.urls')),
    path('api/', include('tasks.urls')),
    path('api/', include('articles.urls')),
    path('api/', include('forum.urls')),
    path('api/', include('interviews.urls')),
    path('api/', include('comments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

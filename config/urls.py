from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

@csrf_exempt
@require_http_methods(["OPTIONS"])
def cors_preflight(request):
    response = HttpResponse()
    response["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response["Access-Control-Allow-Credentials"] = "true"
    return response

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

urlpatterns.append(path('api/<path:path>', cors_preflight))
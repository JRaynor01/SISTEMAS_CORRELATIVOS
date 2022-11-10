from django.contrib import admin
from django.urls import path, include, re_path
from django.conf  import settings
from django.views.static import serve

urlpatterns = [
    path('correlativos/admin/', admin.site.urls),
    path('correlativos/registers/', include("registers.urls")),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root':settings.MEDIA_ROOT,
    })
]

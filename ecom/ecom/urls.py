from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static
from django.conf.urls import handler404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("core.urls", namespace='store')),
    path('account/', include("account.urls", namespace='account')),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

handler404 = "core.views.custom_404"  # noqa: F811

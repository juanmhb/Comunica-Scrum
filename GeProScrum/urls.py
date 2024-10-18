
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Scrum.urls')),
    path('',include('Mensajes.urls')),
    # path('Scrum/',include('Scrum.urls')),
]

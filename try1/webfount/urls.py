"""
URL configuration for webfount project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r"^proxy/(?P<path>.*)$", views.proxy_entry),
    path("sse/<sid>", views.sse_stream),
    path("admin/sessions", views.admin_sessions),
    path("admin/sessions/<sid>", views.admin_edit),
    path("api/room", views.create_room),
    path("api/room/<room>/join", views.join_room),
    path("backend/", admin.site.urls),
]

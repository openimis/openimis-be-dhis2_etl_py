from django.urls import path

from . import views

urlpatterns = [
    path('StartThreadTask', views.start_task, name='start_task')]

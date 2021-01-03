from django.urls import path

from . import views

urlpatterns = [
    path('StartThreadTask', views.startThreadTask, name='startThreadTask'),
    path('CheckThreadTask', views.checkThreadTask, name='checkThreadTask')]

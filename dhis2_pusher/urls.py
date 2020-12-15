from django.urls import path

from . import views

urlpatterns = [
    path('', views.insurees, name='insuree'),
    path('', views.policies, name='policy'),
    path('', views.claims, name='claims'),
]
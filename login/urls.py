from django.urls import path

from . import views

urlpatterns = [
    # login user/
    path('', views.index, name='index'),
    # login user/
    path('client/', views.client, name='client'),
    # login user/
    path('pharm/', views.pharm, name='pharm'),
    # login Admin/
    path('admin/', views.admin, name='admin'),
]

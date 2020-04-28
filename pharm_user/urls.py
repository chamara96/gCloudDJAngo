from django.urls import path

from . import views

urlpatterns = [
    # pharmuser/
    path('', views.index, name='index'),
    # pharmuser/reg/
    path('reg/', views.reg,  name='reg'),
    # view order
    path('vieworder/', views.vieworder, name='vieworder'),
    # get order
    path('getorder/', views.getorder, name='getorder'),
    # get order
    path('viewgetorders/', views.viewgetorders, name='viewgetorders'),
    # update active list
    path('updateactiveorder/', views.updateactiveorder, name='updateactiveorder'),
    # get order
    path('viewpneworder/', views.viewpneworder, name='viewpneworder'),
    # get order
    path('viewpcurrentorder/', views.viewpcurrentorder, name='viewpcurrentorder'),
    # get order
    path('updatepharmarr/', views.updatepharmarr, name='updatepharmarr'),
    # get order
    path('viewanyorder/', views.viewanyorder, name='viewanyorder'),


]

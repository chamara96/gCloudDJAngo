from django.urls import path

from . import views

urlpatterns = [
    # clientuser/
    path('', views.index, name='index'),
    # clientuser/reg/
    # path('reg/<str:name>&<str:tele>&<str:lat>&<str:lng>&<str:address>&<str:password>', views.reg, name='reg'),
    path('reg/', views.reg, name='reg'),
    # clientuser/
    # path('login/<str:username>&<str:password>', views.login, name='login'),
    path('pharmlist/', views.pharmlocations, name='pharmlocations'),
    # client set order
    path('setorder/', views.clientsetorder, name='clientsetorder'),
    # client my current order
    path('mycurrentorder/', views.mycurrentorder, name='mycurrentorder'),

    # client my order history
    path('myorderhistory/', views.myorderhistory, name='myorderhistory'),

    # get hospital data
    path('hospital/', views.hospital, name='hospital'),

    # user confirm final pharmacy
    path('confirmpharm/', views.confirmpharm, name='confirmpharm'),

    # My requested orders
    path('myrequestedorder/', views.myrequestedorder, name='myrequestedorder'),

    # My Confirmed orders
    path('myconfirmedorder/', views.myconfirmedorder, name='myconfirmedorder'),

    # My Past orders
    path('mypastorder/', views.mypastorder, name='mypastorder'),

    # User click 'Completed' button
    path('completeorder/', views.completeorder, name='completeorder'),
    
    # User click 'Cancel Order' button
    path('cancelorder/', views.cancelorder, name='cancelorder'),


]

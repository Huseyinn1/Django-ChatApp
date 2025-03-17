from django.urls import path
from . import views

urlpatterns = [
    path('chat/channels/', views.channel_list, name='channel_list'),
    path('chat/channels/create/', views.create_channel, name='create_channel'),
    path('chat/channels/<int:channel_id>/join/', views.join_channel, name='join_channel'),
    path('chat/channels/<int:channel_id>/leave/', views.leave_channel, name='leave_channel'),
    path('chat/channels/<int:channel_id>/messages/', views.channel_messages, name='channel_messages'),
]
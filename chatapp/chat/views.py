from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import Channel, Message

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def channel_list(request):
    channels = Channel.objects.annotate(members_count=Count('members')).all()
    channels_data = [{
        'id': channel.id,
        'name': channel.name,
        'members_count': channel.members_count,
        'created_by': channel.created_by.username,
        'created_at': channel.created_at
    } for channel in channels]
    return Response(channels_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_channel(request):
    name = request.data.get('name')
    if not name:
        return Response({'error': 'Channel name is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if Channel.objects.filter(name=name).exists():
        return Response({'error': 'Channel with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    channel = Channel.objects.create(name=name, created_by=request.user)
    channel.members.add(request.user)
    
    return Response({
        'id': channel.id,
        'name': channel.name,
        'created_by': channel.created_by.username,
        'created_at': channel.created_at
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_channel(request, channel_id):
    try:
        channel = Channel.objects.get(id=channel_id)
        if request.user not in channel.members.all():
            channel.members.add(request.user)
        return Response({'status': 'success'})
    except Channel.DoesNotExist:
        return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_channel(request, channel_id):
    try:
        channel = Channel.objects.get(id=channel_id)
        if request.user in channel.members.all():
            channel.members.remove(request.user)
        return Response({'status': 'success'})
    except Channel.DoesNotExist:
        return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def channel_messages(request, channel_id):
    try:
        channel = Channel.objects.get(id=channel_id)
        if request.user not in channel.members.all():
            return Response({'error': 'Not a member of this channel'}, status=status.HTTP_403_FORBIDDEN)
        
        messages = Message.objects.filter(channel=channel).order_by('-timestamp')[:50]
        messages_data = [{
            'id': msg.id,
            'content': msg.content,
            'sender': msg.sender.username,
            'timestamp': msg.timestamp
        } for msg in messages]
        return Response(messages_data)
    except Channel.DoesNotExist:
        return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)

def chat_view(request):
    return render(request, 'chat.html')
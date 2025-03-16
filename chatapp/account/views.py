from django.shortcuts import render, redirect
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .exceptions import *
from django.contrib import messages
from django.contrib.auth import  authenticate
from rest_framework.views import APIView


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Kayıt başarılı',
                'tokens': 
                {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Giriş başarılı',
                'tokens': 
                {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
                }
            })
        return Response({
            'status': 'error',
            'message': 'Geçersiz kullanıcı adı veya şifre'
        }, status=status.HTTP_401_UNAUTHORIZED)

def register_view(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            request.session['access_token'] = str(refresh.access_token)
            request.session['refresh_token'] = str(refresh)
            messages.success(request, 'Kayıt başarılı!')
            return redirect('login')
        
        else:
            messages.error(request, 'Kayıt sırasında hata oluştu!')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            request.session['access_token'] = str(refresh.access_token)
            request.session['refresh_token'] = str(refresh)
            return redirect('chat')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre!')
    return render(request, 'login.html')

def chat_view(request):
    return render(request, 'chat.html')

def logout_view(request):
    request.session.pop('access_token', None)
    request.session.pop('refresh_token', None)
    return redirect('login')

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'status': 'success',
            'message': 'Chat sayfasına hoş geldiniz'
        })
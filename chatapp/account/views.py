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
        # Handle both JSON and form data
        data = request.data if isinstance(request.data, dict) else request.POST
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response_data = {
                'status': 'success',
                'message': 'Giriş başarılı',
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token
                }
            }
            
            # If this is a form submission (not API), set session
            if not isinstance(request.data, dict):
                request.session['access_token'] = access_token
                request.session['refresh_token'] = refresh_token
                return redirect('chat')
                
            return Response(response_data)
            
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
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Store tokens in session
            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token
            
            # Also store in cookies for JavaScript access
            response = redirect('chat')
            response.set_cookie('access_token', access_token, httponly=False)
            response.set_cookie('refresh_token', refresh_token, httponly=False)
            return response
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre!')
    return render(request, 'login.html')

def chat_view(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('login')
    
    # Pass the token to the template
    return render(request, 'chat.html', {
        'access_token': access_token,
        'refresh_token': request.session.get('refresh_token')
    })

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

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'username': request.user.username,
            'id': request.user.id
        })
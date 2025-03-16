from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from .exceptions import *
from rest_framework.views import exception_handler

def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthenticationError as e:
            return Response({
                'status': 'error',
                'code': e.status_code,
                'message': str(e.detail),
                'type': 'authentication_error'
            }, status=e.status_code)
            
        except PermissionError as e:
            return Response({
                'status': 'error',
                'code': e.status_code,
                'message': str(e.detail),
                'type': 'permission_error'
            }, status=e.status_code)
            
        except ValidationError as e:
            return Response({
                'status': 'error',
                'code': e.status_code,
                'message': str(e.detail),
                'type': 'validation_error'
            }, status=e.status_code)
            
        except NotFoundError as e:
            return Response({
                'status': 'error',
                'code': e.status_code,
                'message': str(e.detail),
                'type': 'not_found_error'
            }, status=e.status_code)
            
        except ObjectDoesNotExist:
            return Response({
                'status': 'error',
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'İstenen kaynak bulunamadı.',
                'type': 'not_found_error'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except DatabaseError:
            return Response({
                'status': 'error',
                'code': status.HTTP_503_SERVICE_UNAVAILABLE,
                'message': 'Veritabanı hatası oluştu.',
                'type': 'database_error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Beklenmeyen bir hata oluştu.',
                'type': 'internal_server_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper 

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is None:
        response = Response({
            'status': 'error',
            'message': 'Bu sayfaya erişim yetkiniz bulunmamaktadır.',
            'detail': str(exc)
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    return response 
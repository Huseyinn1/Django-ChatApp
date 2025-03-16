from rest_framework.exceptions import APIException
from rest_framework import status

class BaseCustomException(APIException):
    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail, code=code)
        self.detail = detail or self.default_detail
        self.status_code = code or self.status_code

class AuthenticationError(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Kimlik doğrulama başarısız.'
    
class PermissionError(BaseCustomException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Bu işlem için yetkiniz bulunmamaktadır.'

class ValidationError(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Geçersiz veri formatı.'

class NotFoundError(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'İstenen kaynak bulunamadı.'

class ConnectionError(BaseCustomException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Bağlantı hatası oluştu.'

class UnauthorizedAccessError(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Bu sayfaya erişim yetkiniz bulunmamaktadır.' 
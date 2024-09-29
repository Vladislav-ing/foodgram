import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from . import constants


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)

        return super().to_internal_value(data)
    
    
class LimitPageNumberPagination(PageNumberPagination):
    """
    Расширенный базовый пагинатор PageNumber.
    Добавлен параметр limit + опциональное кол. пользователей в response.
    """
    page_size_query_param = 'limit'
    page_size = constants.USERS_PAGE_SIZE
    
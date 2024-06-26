from rest_framework import serializers
from api.util import get_simple_serializer_error

class BaseSerializer(serializers.Serializer):

    def get_simple_error(self):
        return get_simple_serializer_error(self)

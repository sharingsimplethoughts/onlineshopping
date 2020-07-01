from rest_framework.fields import empty
from rest_framework.serializers import(
	 Serializer,
     BooleanField,
	 )
from rest_framework import  pagination
import json
import requests


def get_error(serializer):
    error_keys = list(serializer.errors.keys())
    if error_keys:
        error_msg = serializer.errors[error_keys[0]]
        return error_msg[0]
    return serializer.errors


class CustomBooleanField(BooleanField):
    def get_value(self, dictionary):
        return dictionary.get(self.field_name, empty)
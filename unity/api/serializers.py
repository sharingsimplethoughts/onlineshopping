from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    SerializerMethodField,
    Serializer,
    CharField,
    ChoiceField

)

from ..models import *
from product.models import ProductImageFor3DView



class ImageViewSerializer(ModelSerializer):
    class Meta:
        model = ProductImageFor3DView
        fields = [
            'front',
            'back',
            'wearable_type'
        ]

class UserBodyMeasurementDataSerializer(ModelSerializer):

    class Meta:
        model = UserBodyMeasurementData
        fields = [
            'gender',
            'height',
            'chest',
            'butts',
            'waist',
            'thigh',
            'arm',

        ]

class SaveMeasurementSerializer(Serializer):
    gender = ChoiceField(choices=GENDER ,error_messages={'required': 'gender key is required', 'blank': 'gender is required'})
    height = CharField(error_messages={'required': 'height key is required', 'blank': 'height is required'})
    chest = CharField(error_messages={'required': 'chest key is required', 'blank': 'chest is required'})
    butts = CharField(error_messages={'required': 'butts key is required', 'blank': 'butts is required'})
    waist = CharField(error_messages={'required': 'waist key is required', 'blank': 'waist is required'})
    thigh = CharField(error_messages={'required': 'thigh key is required', 'blank': 'thigh is required'})
    arm = CharField(error_messages={'required': 'arm key is required', 'blank': 'arm is required'})
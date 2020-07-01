from rest_framework.generics import (
		CreateAPIView,
		ListAPIView
	)
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import *
from .serializers import *
from common.common_func import get_error
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated
from common.common_func import get_error


class DefaultSizeAPIView(APIView):

    def get(self, request):
        user_id = request.GET.get('user_id')
        product_id = request.GET.get('product_id', None)
        color_id = request.GET.get('color_id', None)
        if user_id:
            qs = UserBodyMeasurementData.objects.filter(user_id =user_id).order_by('-created_on')
            if qs.exists():
                data = UserBodyMeasurementDataSerializer(qs.first()).data
            else:
                data = {
                    "gender": "2",
                    "height": "0",
                    "chest": "110",
                    "butts": "1000",
                    "waist": "90",
                    "thigh": "75",
                    "arm": "0",
                }
            if product_id =='':
                product_id =0
            if color_id=='':
                color_id =0
            img_qs = ProductImageFor3DView.objects.filter(product=product_id, colour = color_id)

            img_data =  ImageViewSerializer(img_qs.first(),context={'request':request}).data
            data['images']=img_data
            return Response({
                'data':data
            })

        return Response({'message': 'product id and user id both are required'}, 400)


class SaveMeasurementAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self,request):
        data = request.data
        user = request.user
        serializer = SaveMeasurementSerializer(data=data)
        if serializer.is_valid():
            UserBodyMeasurementData.objects.create(user = user, gender=data['gender'],height=data['height'],
                                                   chest=data['chest'], butts=data['butts'], waist=data['waist'],
                                                   thigh = data['thigh'], arm=data['arm'])

            return Response({'message':'saved successfully'},200)
        return Response({'message':get_error(serializer)})


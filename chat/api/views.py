from push_notifications.models import GCMDevice
from rest_framework.exceptions import APIException
from rest_framework.generics import (
		CreateAPIView,
		ListAPIView
	)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from accounts.api.serializers import APIException403
from common.celery_tasks import send_call_notification
from ..models import *
import subprocess
from pathlib import Path
from PIL import Image

class UploadMediaAPIView(APIView):

    def post(self, request):
        data = request.FILES
        image = data.get('image',None)
        image_url = ""
        parent = Path(os.getcwd()).parent
        if image:
            img_obj = MediaFile.objects.create(file=image)
            # subprocess.Popen(['ffmpeg', '-y', '-i', '{}'.format(os.path.basename(img_obj.file.name)), '-ss', '00:00:00.000', '-vframes', '1',
            #                  'output.jpg'], cwd='{}/media_cdn/chat_media'.format(Path(os.getcwd()).parent))
            # img = Image.open('{}/media_cdn/chat_media/output.jpg'.format(parent))
            # img_obj.thumb = img
            # img_obj.save()
        else:
            return Response({
                'message':'Please Provide at least one media file'
            },400)

        data ={
            'image_url':img_obj.file.url,
        }

        return Response({
            'data':data
        },200)


class SendNotificationCall(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        print(data)
        user_ids = data['channel_name'].split('_')
        user_id = str(request.user.id)
        if not user_id in user_ids:
            raise APIException403({'message': "User doesn't exists"})
        if user_id == user_ids[0]:
            opp_user_id = user_ids[1]
        else:
            opp_user_id = user_ids[0]
        data['user_id'] = user_id
        data['opp_user_id'] = opp_user_id
        send_call_notification(**data)
        return Response({
            'message': 'Notification Sent Successfully',
            'success': 'True'
        }, status=200, )

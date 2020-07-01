from django.urls import path

from .views import *

urlpatterns = [

    path('upload_media', UploadMediaAPIView.as_view(), name="UploadMediaAPIView"),
    path('send_notification_for_call', SendNotificationCall.as_view(), name="sendNotificationForCall"),

]
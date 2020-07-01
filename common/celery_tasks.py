from celery import shared_task
from django.template.loader import render_to_string
from django.core import mail
from push_notifications.models import GCMDevice

from accounts.models import User
from Shopping.settings import BASE_URL
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from accounts.tokens import account_activation_token

from authy.api import AuthyApiClient
authy_api = AuthyApiClient('jhkj')
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
from .firebase import createUserNode, updateUserNode, deleteUserNode, updateOnlineStatus

NOTIFICATION_TYPE = (('1','Voice Call'), ('2', 'Video Call'))

#notification send
@shared_task(track_started=True)
def send_call_notification(**kwargs):
    userObj = User.objects.get(int(kwargs['user_id']))
    if kwargs['notification_type'] == '1':
        title = 'Incoming Voice Call'
    elif kwargs['notification_type'] == '2':
        title = 'Incoming Video Call'
    
    try:
        GCMDevice.objects.get(user__id=int(kwargs['opp_user_id'])).send_message(
            None,
            extra={
                'title': title,
                'body': 'Incoming call from {} {}'.format(userObj.first_name, userObj.last_name),
                'misc': kwargs
            }
        )
    except Exception as e:
        print(str(e))

@shared_task(track_started=True)
def create_user_node(name, id, profile_image ,role):
    print('ok')
    createUserNode(name, id, profile_image,role)
    print('okkk')
    return 'successfully created user node'


@shared_task(track_started=True)
def update_user_node(name, id, profile_image):
    updateUserNode(name ,id, profile_image)
    return 'successfully updated user node'


@shared_task(track_started=True)
def delete_user_node(id):
    deleteUserNode(id)
    return 'successfully deleted user node'


@shared_task(track_started=True)
def update_user_online_node(id,status):
    updateOnlineStatus(id,status)
    return 'status updated'


@shared_task(track_started=True)
def send_email_verify_mail(user_id):
    user_obj = User.objects.get(id=user_id)

    subject = 'Activate Your Viewed Account'
    to = user_obj.email
    plain_message = None
    from_email = 'Viewed <webmaster@localhost>'
    message_text = render_to_string('account_activation/account_activation_email.html', {
        'user': user_obj,
        'domain': BASE_URL,
        'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)).decode(),
        'token': account_activation_token.make_token(user_obj),
    })
    mail.send_mail(subject, plain_message, from_email, [to], html_message=message_text)

    return 'success..!!'


@shared_task(track_started=True)
def send_phone_verify_otp(country_code, mobile_number ):
    request = authy_api.phones.verification_start(mobile_number, country_code,
    									via='sms', locale='en')
    if request.content['success'] == True:
        return 'successfully send message'
    else:
        return 'faild to send message' + request.content['message']




from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from accounts.tokens import account_activation_token
from .models import UserOtherInfo
# Create your views here..

from django.views import View

User = get_user_model()


def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and account_activation_token.check_token(user, token):

		usrObj = UserOtherInfo.objects.get(user=user)
		usrObj.ismailverify = True
		usrObj.save()
		return HttpResponse("Your account is successfully Activated")
	else:
		return HttpResponse("Invalid token")


class ServiceWorkerView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'fcm/firebase-messaging-sw.js', content_type="application/x-javascript")
from django.shortcuts import render
import datetime
# Create your views here.
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.models import *
from requests import Response
from rest_framework.exceptions import APIException

from Shopping.settings import USER_PERMISSIONS
from .forms import *
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator

from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from accounts.api.password_reset_form import MyPasswordResetForm
from accounts.models import *
from .models import *
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from accounts.decorator import *

from common.celery_tasks import create_user_node, update_user_online_node
from common.firebase import createUserNode
from product.models import WEARABLE_TYPE
from product.models import ProductImageFor3DView
from push_notifications.models import GCMDevice

from rest_framework_jwt.settings import api_settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class AdminLoginView(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm
        if request.user.is_authenticated:
            # update online status
            # update_user_online_node.delay(request.user.id, True)
            return HttpResponseRedirect('/admin/users/home/')

        return render(request, 'admin-interface/accounts/login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            deviceToken = form.cleaned_data['deviceToken']
            userother_obj = UserOtherInfo.objects.select_related('role', 'user').get(user__email=request.POST['email'])
            role = userother_obj.role.role_id
            if role == '2':  # admin
                name = userother_obj.user.first_name + ' ' + userother_obj.user.last_name
                if userother_obj.profileimg:

                    profile_image = userother_obj.profileimg.url
                else:
                    profile_image = ''
            else:  # sub-admin
                try:
                    prof_obj = Profile.objects.get(user=userother_obj.user)

                    name = prof_obj.name
                    if prof_obj.profileimg:
                        profile_image = prof_obj.profileimg.url
                    else:
                        profile_image = ''
                except:
                    name = ''
                    profile_image = ''

            # update device_token
            userother_obj.device_token=deviceToken
            userother_obj.save()

            previous_device_token = GCMDevice.objects.filter(registration_id=deviceToken)
            if previous_device_token.exists():
                previous_device_token.update(registration_id='')
                previous_device_user = UserOtherInfo.objects.filter(device_token=deviceToken).exclude(id=userother_obj.user.id)
                previous_device_user.update(registration_id='')
            gcm_device, created = GCMDevice.objects.get_or_create(user=userother_obj.user, cloud_message_type='FCM')
            gcm_device.registration_id = deviceToken
            gcm_device.is_active = True
            gcm_device.save()


            # update sub admin node
            payload = jwt_payload_handler(userother_obj.user)
            token = jwt_encode_handler(payload)
            print(token)
            login(request, userother_obj.user)
            app_in_userprofile = Profile.objects.filter(user=userother_obj.user)
            if app_in_userprofile.exists():
                createUserNode(name, userother_obj.user.id, profile_image, role)
            # createUserNode(name, userother_obj.user.id, profile_image, role)
            response = HttpResponseRedirect('/admin/users/home')
            response.set_cookie('role', role, 63072000)
            response.set_cookie('jwt', token)
            user_permissions = list(UserPermissions.objects.get(user=userother_obj.user).permission.all().values_list('permission_id', flat=True))
            print(user_permissions)
            for _ in USER_PERMISSIONS:
                if int(_[0]) in user_permissions:
                    response.set_cookie('permission_{}'.format(_[0]), True, 63072000)
            return response

        return render(request, 'admin-interface/accounts/login.html', {'form': form})


class AudioManagementView1(View):
    def get(self, request):
        return render(request, 'admin-interface/chat_management/audio_management.html')


class AudioManagementView2(View):
    def get(self, request):
        return render(request, 'admin-interface/chat_management/audio_management2.html')


class AudioManagementView3(View):
    def get(self, request):
        return render(request, 'admin-interface/chat_management/audio_management3.html')


class VideoCallView(View):
    def get(self, request, *args, **kwargs):
        channel_id = self.kwargs['channel_id'].split('_')
        user_id = str(request.user.id)
        if not user_id in channel_id:
            raise APIException({'message': 'OOPS!! Something went wrong'})
        if user_id == channel_id[0]:
            opp_user_id = channel_id[1]
        else:
            opp_user_id = channel_id[0]
        opp_user_profile = User.objects.filter(id=int(opp_user_id))
        return render(request, 'admin-interface/chat_management/video_call_screen.html', {'channel_id': self.kwargs['channel_id'], 'opp_user_profile': opp_user_profile[0], 'audio': True, 'video': True})


class AudioCallView(View):
    def get(self, request, *args, **kwargs):
        channel_id = self.kwargs['channel_id'].split('_')
        user_id = str(request.user.id)
        if not user_id in channel_id:
            raise APIException({'message': 'OOPS!! Something went wrong'})
        if user_id == channel_id[0]:
            opp_user_id = channel_id[1]
        else:
            opp_user_id = channel_id[0]
        opp_user_profile = User.objects.filter(id=int(opp_user_id))
        return render(request, 'admin-interface/chat_management/video_call_screen.html', {'channel_id': self.kwargs['channel_id'], 'opp_user_profile': opp_user_profile[0], 'audio': True, 'video': False})


class LogoutView(View):

    def get(self, request):
        logout(request)

        response = HttpResponseRedirect('/admin/users/login/')
        response.delete_cookie('role')
        response.delete_cookie('jwt')
        for _ in range(1,9):
            response.delete_cookie('permission_{}'.format(_))
        return response


class ResetPasswordView(auth_views.PasswordResetView):
    form_class = MyPasswordResetForm


class ChangePasswordView(View):

    def get(self, request):
        form = ChangePasswordForm(user=request.user)
        return render(request, 'admin-interface/accounts/change_password.html', {'form': form})

    def post(self, request):
        user = request.user
        print(request.POST)
        form = ChangePasswordForm(request.POST or None, user=request.user)

        if form.is_valid():
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            # messages.success(request, 'Your password have been changed successfully. Please login again to access account')
            return HttpResponseRedirect('/admin/users/login/')
        return render(request, 'admin-interface/accounts/change_password.html', {'form': form})


class AdminHomeView(View):
    @dashboard_permission_required
    def get(self, request, *args, **kwargs):


        context = {
            'home': 'home'

        }
        return render(request, 'admin-interface/home.html', context)


class AdminProfileView(View):

    def get(self, request, *args, **kwargs):
        user = request.user
        form = AdminProfileEditForm
        try:
            userotherinfo = UserOtherInfo.objects.get(user=user)
        except:
            userotherinfo = None
        context = {

            'form': form,
            'email': user.email,
            'name': user.first_name + ' ' + user.last_name,
            'user_other_info': userotherinfo

        }

        return render(request, 'admin-interface/accounts/admin_profile.html', context)


class AdminProfileEditView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        form = AdminProfileEditForm
        try:
            userotherinfo = UserOtherInfo.objects.get(user=user)
        except:
            userotherinfo = None
        context = {

            'form': form,
            'email': user.email,
            'firstname': user.first_name,
            'lastname': user.last_name,
            'phonenumber': userotherinfo.phonenum,

            'user_other_info': userotherinfo

        }
        return render(request, 'admin-interface/accounts/admin_profile_change.html', context)

    def post(self, request, *args, **kwargs):

        print(request.POST)

        user = request.user
        try:
            userotherinfo = UserOtherInfo.objects.get(user=user)
        except:
            userotherinfo = None
        form = AdminProfileEditForm(request.POST or None, user=request.user, userotherinfo=userotherinfo)
        # try:
        #     userotherinfo = UserOtherInfo.objects.get(user=user)
        # except:
        #     userotherinfo = None
        if form.is_valid():

            user = request.user
            email = form.cleaned_data['email']
            phonenumber = form.cleaned_data['phonenumber']
            address = form.cleaned_data['address']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            about = form.cleaned_data['about']
            profile_img = request.FILES.get('profileimg')
            cover_img = request.FILES.get('coverimg')
            print(profile_img, cover_img)

            user.email = email
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            Userotherinfo = UserOtherInfo.objects.get(user=user)
            print(Userotherinfo)
            Userotherinfo.phonenum = phonenumber
            Userotherinfo.addr_one = address
            Userotherinfo.about = about

            if profile_img is not None:
                print('ok')
                Userotherinfo.profileimg = request.FILES.get('profileimg')
            if cover_img is not None:
                print('ok')
                Userotherinfo.coverimg = request.FILES.get('coverimg')
            Userotherinfo.save()
            return HttpResponseRedirect('/admin/users/admin_profile/')

        context = {

            'form': form,
            'email': request.POST.get('email'),
            'firstname': user.first_name,
            'lastname': user.last_name,
            'phonenumber': request.POST.get('phonenumber'),
            'user_other_info': userotherinfo
        }

        return render(request, 'admin-interface/accounts/admin_profile_change.html', context)


class AdminMemberView(View):

    def get(self, request, *args, **kwargs):
        form = AddmMemberForm
        user = request.user
        if user.is_staff:
            role = [1, 2]

            userotherinfos = UserOtherInfo.objects.exclude(role__in=role)
            for userotherinfo in userotherinfos:
                user = User.objects.get(id=userotherinfo.user.id)
                userotherinfo.userb = user

            context = {
                'form': form,
                'user_other_info': userotherinfos,

            }
            return render(request, 'admin-interface/member_management/member_list.html', context)
        return render(request, 'admin-interface/accounts/permission_denied.html')

    def post(self, request, *args, **kwargs):
        user = request.user
        print(request.POST)
        form = AddmMemberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            phonenumber = form.cleaned_data['phonenumber']
            region = form.cleaned_data['region']
            address = form.cleaned_data['address']

        return HttpResponse('false')


class AdminUserListView(View):
    @account_permission_required
    def get(self, request, *args, **kwargs):
        # app_users   = User.objects.filter(is_staff = False)
        app_users = UserOtherInfo.objects.filter(role=1).select_related('user')
        # for app_users in app_users:
        # 	user = User.objects.get(id = userotherinfo.user.id)
        # 	userotherinfo.userb = user
        context = {

            'users': app_users
        }
        return render(request, 'admin-interface/user_management/user_list.html', context)

    # @account_permission_required
    # def post(self, request, *args, **kwargs):
    #     print(request.POST.get('android'))
    #     app_users = UserOtherInfo.objects.filter(role=1).select_related('user')
    #     context = {
    #
    #         'users': app_users
    #     }
    #     return render(request, 'admin-interface/user_management/user_list.html', context)
class AdminStylistListView(View):
    @member_permission_required
    def get(self, request, *args, **kwargs):
        stylist = UserOtherInfo.objects.filter(role=4).select_related('user').order_by('user__first_name')

        context = {

            'stylists': stylist
        }

        return render(request, 'admin-interface/stylist_management/stylist_list.html', context)


class AdminDesignerListView(View):
    @member_permission_required
    def get(self, request, *args, **kwargs):
        designer = UserOtherInfo.objects.filter(role=3).select_related('user').order_by('user__first_name')
        print(designer)

        context = {

            'designers': designer
        }

        return render(request, 'admin-interface/designer_management/designer_list.html', context)


class AdminManufacturerListView(View):
    @member_permission_required
    def get(self, request, *args, **kwargs):
        manufacturer = UserOtherInfo.objects.filter(role=5).select_related('user').order_by('user__first_name')

        context = {

            'manufacturers': manufacturer
        }

        return render(request, 'admin-interface/manufacturer_management/manufacturer_list.html', context)


class addNewUserView(View):

    def get(self, request, *args, **kwargs):
        role = self.kwargs['role']

        if role == 5:
            return render(request, 'admin-interface/manufacturer_management/addmf.html')
        if role == 3:
            return render(request, 'admin-interface/designer_management/addds.html')
        if role == 4:
            return render(request, 'admin-interface/stylist_management/addst.html')


class EditNewUserView(View):
    @member_permission_required
    def get(self, request, *args, **kwargs):
        profile_id = self.kwargs['profile_id']
        role = self.kwargs['role']
        user = UserOtherInfo.objects.select_related('user').get(role=role, pk=profile_id)
        try:
            permissions = UserPermissions.objects.prefetch_related('permission').get(user=user.user)
            permission_arry = permissions.permission.all().values_list('permission_id', flat=True)
            print(permission_arry)
        except:
            permission_arry = []
        context = {

            'userdata': user,
            'email': user.user.email,
            'phonenumber': user.phonenum,
            'permissions': list(permission_arry),
        }
        if role == 5:
            return render(request, 'admin-interface/manufacturer_management/editmf.html', context)
        if role == 3:
            return render(request, 'admin-interface/designer_management/editds.html', context)
        if role == 4:
            return render(request, 'admin-interface/stylist_management/editst.html', context)

    @member_permission_required
    def post(self, request, *args, **kwargs):
        profile_id = self.kwargs['profile_id']
        role = self.kwargs['role']
        print(request.POST)
        userotherinfo = UserOtherInfo.objects.select_related('user').get(pk=profile_id)
        form = AdminMemberEditForm(data=request.POST or None, user_id=profile_id, user=userotherinfo.user)


        print(userotherinfo, '1')

        print(form.is_valid())
        if form.is_valid():
            user = userotherinfo.user
            print(user)

            email = form.cleaned_data['email']
            phonenumber = form.cleaned_data['phonenumber']
            countrycode = form.cleaned_data['countrycode']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']
            status = form.cleaned_data['status']

            if status == 'active':
                status = True
            else:
                status = False

            user.email = email
            user.first_name = firstname
            user.last_name = lastname
            user.is_active = status
            user.save()
            print(userotherinfo, 'obj')

            userotherinfo.phonenum = phonenumber
            print('ok')
            userotherinfo.country_code = countrycode

            userotherinfo.addr_one = address
            userotherinfo.gender = gender

            if request.FILES.get('profileimg') is not None:
                userotherinfo.profileimg = request.FILES.get('profileimg')

            userotherinfo.save()
            print('okkkkkkkkkkkkkkkkk')
            print('righs', *request.POST.getlist('rights'))
            try:
                userpermission = UserPermissions.objects.get(user=user).delete()
                userpermission = UserPermissions.objects.create(user=user)
                userpermission.permission.add(*request.POST.getlist('rights'))

            except:
                userpermission = UserPermissions.objects.create(user=user)
                userpermission.permission.add(*request.POST.getlist('rights'))

            if role == 5:
                return HttpResponseRedirect('/admin/users/manufacturer_list/')
            if role == 3:
                return HttpResponseRedirect('/admin/users/designer_list/')
            if role == 4:
                return HttpResponseRedirect('/admin/users/stylist_list/')

        user = UserOtherInfo.objects.select_related('user').get(role=role, pk=profile_id)
        try:
            permissions = UserPermissions.objects.prefetch_related('permission').get(user=user.user)
            permission_arry = permissions.permission.all().values_list('permission_id', flat=True)
            print(permission_arry)
        except:
            permission_arry = []

        context = {

            'form': form,
            'email': request.POST.get('email'),
            'phonenumber': request.POST.get('phonenumber'),
            'userdata': user,
            'permissions': list(permission_arry),

        }

        if role == 5:
            return render(request, 'admin-interface/manufacturer_management/editmf.html', context)
        if role == 3:
            return render(request, 'admin-interface/designer_management/editds.html', context)
        if role == 4:
            return render(request, 'admin-interface/stylist_management/editst.html', context)


class UserdetailView(View):
    @account_permission_required
    def get(self, request, *args, **kwargs):
        profile_id = self.kwargs['profile_id']
        user = UserOtherInfo.objects.select_related('user').get(pk=profile_id)
        context = {

            'userdata': user

        }

        return render(request, 'admin-interface/user_management/userprofile.html', context)


class MemberdetailView(View):
    @member_permission_required
    def get(self, request, *args, **kwargs):

        profile_id = self.kwargs['profile_id']
        user = UserOtherInfo.objects.select_related('user').get(pk=profile_id)
        print(user.role_id)
        if user.role_id == 3:
            usertype = 'Designer'
            url = 'designer_list'
        elif user.role_id == 4:
            usertype = 'Stylist'
            url = 'stylist_list'

        else:
            usertype = 'Manufacturer'
            url = 'manufacturer_list'

        try:
            userpermission = UserPermissions.objects.get(user=user.user)

        except:

            userpermission = UserPermissions.objects.none()

        try:
            permission = userpermission.permission.all()

        except:
            permission = []

        print(userpermission)
        context = {

            'userdata': user,
            'usertype': usertype,
            'url': url,
            'permissions': permission

        }

        return render(request, 'admin-interface/member_detail.html', context)


class MemberDateFilterView(View):
    def get(self, request, *args, **kwargs):
        role = self.kwargs['role']
        print(request.GET)

        start_date = datetime.datetime.strptime(request.GET.get('startdate'), '%m/%d/%Y').strftime('%Y-%m-%d')

        end_date = datetime.datetime.strptime(request.GET.get('enddate'), '%m/%d/%Y').strftime('%Y-%m-%d')

        context = {}
        filterdata = UserOtherInfo.objects.filter(role=role, created__range=(start_date, end_date)).select_related(
            'user').order_by('user__first_name')

        print(filterdata)
        if role == 5:
            context['manufacturers'] = filterdata
            return render(request, 'admin-interface/manufacturer_management/manufacturer_list.html', context)
        if role == 3:
            context['designers'] = filterdata
            return render(request, 'admin-interface/designer_management/designer_list.html', context)
        if role == 4:
            context['stylists'] = filterdata
            return render(request, 'admin-interface/stylist_management/stylist_list.html', context)
        if role == 1:
            context['users'] = filterdata
            return render(request, 'admin-interface/user_management/user_list.html', context)


from designer_stylist.models import *

import firebase_admin

firebase_admin.get_app()
from firebase_admin import db
import logging

logger = logging.getLogger('accounts')


class AppInProfileCreateView(View):

    def get(self, request, *args, **kwargs):
        user = request.user
        role = UserOtherInfo.objects.values_list('role', flat=True).get(user=user)
        # userdata   =  Profile.objects.filter(user=user).first()
        try:
            achievement = Achievement.objects.filter(designerprofile__user=user).select_related(
                'designerprofile').first()
            userdata = achievement.designerprofile
            achievement_img = Image.objects.filter(achievement=achievement)
            print(role)
        except:
            achievement = None
            userdata = None
            achievement_img = None

        context = {

            'usertype': role,
            'userdata': userdata,
            'achievement': achievement,
            'achievement_img': achievement_img

        }

        return render(request, 'admin-interface/appin_profile.html', context)

    def post(self, request, *args, **kwargs):

        form = AppInProfileCreateForm(data=request.POST or None, files=request.FILES)

        print(request.POST)
        print(form.is_valid())
        role = self.kwargs['role']
        profile_id = self.kwargs.get('profile_id')

        if form.is_valid():

            obj = Profile.objects.create(user=request.user, role=role, name=form.cleaned_data.get('name'),
                                         email=form.cleaned_data.get('email'),
                                         profileimg=request.FILES.get('profileimg'),
                                         coverimg=request.FILES.get('coverimg'))
            user_node_db = db.reference('users')
            logger.debug(obj.profileimg.url)
            user_id = 'user_{}'.format(str(request.user.id))
            user_node_db.child(user_id).update({
                'profilePic': obj.profileimg.url,
                'name': obj.name
            })

            year = datetime.datetime.strptime(form.cleaned_data.get('year'), '%m/%d/%Y').strftime('%Y-%m-%d')
            print(year)
            ach_obj = Achievement.objects.create(designerprofile=obj, title=form.cleaned_data.get('title'),
                                                 about=form.cleaned_data.get('about'), year=year, )

            for f in request.FILES.getlist('achievement_images'):
                Image.objects.create(achievement=ach_obj, image=f)

            messages.success(request, 'Your App in profile created successfully')

            return HttpResponseRedirect('/admin/users/appin_profile/' + str(role))

        context = {
            'form': form,

            'email': request.POST.get('email'),

        }

        return render(request, 'admin-interface/appin_profile.html', context)


class AppInProfileEditView(View):

    def get(self, request, *args, **kwargs):
        role = self.kwargs['role']
        return HttpResponseRedirect('/admin/users/appin_profile/' + str(role))

    def post(self, request, *args, **kwargs):
        role = self.kwargs.get('role')
        profile_id = self.kwargs.get('profile_id')
        print(request.POST)

        form = AppInProfileEditForm(data=request.POST or None)
        print(form.is_valid())

        if form.is_valid():

            profileimg = request.FILES.get('profileimg')
            coverimg = request.FILES.get('coverimg')

            obj = Profile.objects.get(pk=profile_id)

            obj.name = form.cleaned_data.get('name')
            obj.email = form.cleaned_data.get('email')

            if profileimg is not None:
                obj.profileimg = profileimg
                user_node_db = db.reference('users')
                user_id = 'user_{}'.format(str(request.user.id))
                user_node_db.child(user_id).update({'profilePic': obj.profileimg.url, 'name': obj.name})
            if coverimg is not None:
                obj.coverimg = coverimg

            obj.save()

            ach_obj = Achievement.objects.get(designerprofile=obj)

            ach_obj.title = form.cleaned_data.get('title')
            ach_obj.about = form.cleaned_data.get('about')
            ach_obj.year = datetime.datetime.strptime(form.cleaned_data.get('year'), '%m/%d/%Y').strftime('%Y-%m-%d')

            ach_obj.save()

            for f in request.FILES.getlist('achievement_images'):
                Image.objects.create(achievement=ach_obj, image=f)

            messages.success(request, 'Your App in profile updated successfully')

            return HttpResponseRedirect('/admin/users/appin_profile/' + str(role))

        role = UserOtherInfo.objects.values_list('role', flat=True).get(user=request.user)
        achievement = Achievement.objects.filter(designerprofile__user=request.user).select_related(
            'designerprofile').first()
        userdata = achievement.designerprofile
        achievement_img = Image.objects.filter(achievement=achievement)

        context = {
            'form': form,
            'usertype': role,
            'userdata': userdata,
            'achievement': achievement,
            'achievement_img': achievement_img

        }

        return render(request, 'admin-interface/appin_profile.html', context)


class StylistDesignerSectionCreateView(View):

    def post(self, request, *args, **kwargs):
        user = request.user
        print(user)

        data = request.POST
        print(data)
        form = StylistDesignerSectionForm(data=data or None)
        print(form.is_valid())
        if form.is_valid():
            StylistDesignerSection.objects.create(user=user, name=data['name'].upper())
            messages.success(request, 'Your section is created successfully !')

            return HttpResponseRedirect('/admin/users/collection/')

        messages.warning(request, 'Please enter a valid section name !')
        return HttpResponseRedirect('/admin/users/collection/')


class StylistDesignerSectionEditView(View):

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.POST
        section_id = self.kwargs.get('section_id')
        form = StylistDesignerSectionForm(data=data or None)
        if form.is_valid():
            print()
            obj = StylistDesignerSection.objects.get(id=section_id)
            obj.name = request.POST['name'].upper()
            obj.save()
            messages.success(request, 'Your section is updated successfully !')

            return HttpResponseRedirect('/admin/users/collection/')
        messages.warning(request, 'Please enter a valid section name !')
        return HttpResponseRedirect('/admin/users/collection/')


from product.models import *


class StylistDesignerCollectionView(View):

    def get(self, request, *args, **kwargs):
        usertype = UserOtherInfo.objects.values_list('role', flat=True).get(user=request.user)

        sections = StylistDesignerSection.objects.filter(user=request.user)

        for section in sections:
            section.products = Product.objects.filter(usersection=section, is_deleted=False).select_related(
                'usercategory')

        context = {
            'usertype': usertype,
            'sections': sections
        }

        return render(request, 'admin-interface/appin_collection.html', context)


class StylistDesignerSelectExistingProduct(View):

    def get(self, request, *args, **kwargs):
        user = request.user

        products = Product.objects.filter(user=user, is_deleted=False)

        context = {
            'products': products

        }
        return render(request, 'admin-interface/section_select_product.html', context)


class StylistDesignerProductList(View):
    @product_permission_required
    def get(self, request, *args, **kwargs):
        user = request.user
        category = Category.objects.all()
        products = Product.objects.filter(user=user, is_deleted=False).order_by('-created_date')

        context = {
            'products': products,
            'categories': category

        }
        return render(request, 'admin-interface/product_management/product_list.html', context)


from designer_stylist.models import StylistDesignerCategory as DSCategory


class StylistDesignerCategory(View):

    def get(self, request, *args, **kwargs):
        user = request.user

        categories = DSCategory.objects.filter(user=user)

        context = {

            'categories': categories
        }

        return render(request, 'admin-interface/product_management/addcategory.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST['name']
        form = StylistDesignerCategoryForm(request.POST or None)
        if form.is_valid():
            try:
                DSCategory.objects.create(user=request.user, name=data)

            except:

                messages.error(request, 'Something went wrong')
                return render(request, 'admin-interface/product_management/addcategory.html')

            messages.success(request, 'Category added successfully')
            return HttpResponseRedirect('/admin/users/add_category/')
        messages.error(request, 'Please enter a valid category name')
        return HttpResponseRedirect('/admin/users/add_category/')


class StylistDesignerAddProduct(View):

    def get(self, request, *args, **kwargs):
        category = Category.objects.all()
        dscategory = DSCategory.objects.filter(user=request.user)
        section = StylistDesignerSection.objects.filter(user=request.user)
        print(category, dscategory)

        section_id = request.GET.get('section_id')
        if section_id != '' and section_id != None:
            backurl = '/admin/users/collection/'
        else:
            backurl = '/admin/users/product_list/'

        context = {
            'categories': category,
            'ownCategories': dscategory,
            'section': section,
            'backurl': backurl,

        }

        return render(request, 'admin-interface/product_management/addproduct.html', context)

    def post(self, request, *args, **kwargs):

        data = request.POST
        print(data)

        form = ProductCreateForm(request.POST or None)
        if request.FILES.get('main_img') is None:
            form.add_error(None, "Please select a main product image")

        if form.is_valid():

            category = Category.objects.get(pk=data['category'])
            subcategory = SubCategory.objects.get(pk=data['subcategory'])
            subsubcategory = SubSubCategory.objects.get(pk=data['subsubcategory'])

            if data.get('owncategory') != '' and data.get('owncategory') != None:
                owncategory = DSCategory.objects.get(pk=data.get('owncategory'))
            else:
                owncategory = None

            if form.cleaned_data.get('new_from') != '' and form.cleaned_data.get('new_to') != '':
                new_from = datetime.datetime.strptime(form.cleaned_data.get('new_from'), '%m/%d/%Y').strftime(
                    '%Y-%m-%d')
                new_to = datetime.datetime.strptime(form.cleaned_data.get('new_to'), '%m/%d/%Y').strftime('%Y-%m-%d')
            else:
                new_from = None
                new_to = None

            role = UserOtherInfo.objects.filter(user=request.user).first().role.id

            prod_obj = Product.objects.create(name=data['name'].capitalize(), category=category,
                                              subcategory=subcategory,
                                              subsubcategory=subsubcategory, user=request.user, user_role=role,
                                              usercategory=owncategory,
                                              description=data['des'].capitalize(),
                                              more_info=data['more_info'].capitalize(),
                                              pattern=data['pattern'].capitalize(),
                                              material=data['material'].capitalize(), fit=data['fit'].capitalize(),
                                              main_img=request.FILES.get('main_img'), brand=data['brand'],
                                              new_from=new_from, new_to=new_to, )

            section_id = request.GET.get('section_id')

            if section_id != '' and section_id != None:
                prod_obj.usersection.add(section_id)
                messages.success(request, 'Added successfully. Please add other Variants')
                return HttpResponseRedirect(
                    '/admin/users/add_product_varients/' + str(prod_obj.id) + '?section_id=' + section_id)

            messages.success(request, 'Added successfully. Please add other Variants')
            return HttpResponseRedirect('/admin/users/add_product_varients/' + str(prod_obj.id))

        category = Category.objects.all()
        dscategory = DSCategory.objects.filter(user=request.user)
        section = StylistDesignerSection.objects.filter(user=request.user)

        section_id = request.GET.get('section_id')
        if section_id != '' and section_id != None:
            backurl = '/admin/users/collection/'
        else:
            backurl = '/admin/users/product_list/'

        context = {
            'form': form,
            'categories': category,
            'ownCategories': dscategory,
            'section': section,
            'name': data['name'],
            'des': data['des'],
            'pattern': data['pattern'],
            'more_info': data['more_info'],
            'material': data['material'],
            'brand': data['brand'],
            'fit': data['fit'],
            'backurl': backurl,
            'new_from': data['new_from'],
            'new_to': data['new_to'],

        }

        return render(request, 'admin-interface/product_management/addproduct.html', context)


def sum_of_qty(qty_list):
    total_sum = 0
    for element in qty_list:
        total_sum = total_sum + int(element)
    return total_sum


class StylistDesignerAddProductVarientsView(View):
    def get(self, request, *args, **kwargs):

        prod_obj = Product.objects.get(id=self.kwargs.get('product_id'))
        wearbale_type = WEARABLE_TYPE
        context = {
            'product_id': self.kwargs.get('product_id'),
            'colours': Colour.objects.all().exclude(
                id__in=prod_obj.available_colours.filter(is_active=True).values('colour')),
            'wearable_types': wearbale_type
        }
        return render(request, 'admin-interface/product_management/add_sub_product.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        product_id = self.kwargs.get('product_id')
        form = AddProductVarientsForm(data or None)
        if request.FILES.getlist('product_img') == []:
            form.add_error(None, "Please select some product images")

        if len(data.getlist('size')) != len(set(data.getlist('size'))):
            form.add_error(None, "You can not select same size more than one")

        prod_obj = Product.objects.get(id=product_id)
        if form.is_valid():

            if prod_obj:

                actual_price = data['price']
                special_price = data.get('special_price')

                if special_price == '':
                    special_price = actual_price
                    offer = 0
                else:
                    offer = ((int(data['price']) - int(special_price)) * 100 // int(data['price']))

                size_list = []
                for i in range(len(data.getlist('qty'))):
                    size = data.getlist('size')[i]
                    qty = data.getlist('qty')[i]

                    if size == 'XS':
                        sort_id = 1
                    elif size == 'S':
                        sort_id = 2
                    elif size == 'M':
                        sort_id = 3
                    elif size == 'L':
                        sort_id = 4
                    elif size == 'XL':
                        sort_id = 5
                    elif size == 'XXL':
                        sort_id = 6
                    elif size == 'XXXL':
                        sort_id = 7

                    obj = ProductSizeWithQty.objects.create(size=size, initial_qty=qty, available_qty=qty,
                                                            sort_id=sort_id)
                    print(obj, 'size obj')
                    size_list.append(obj)

                prod_col_obj = ProductAvailableColourWithSizeQty.objects.create(colour_id=data['colour'],
                                                                                actual_price=data['price'],
                                                                                special_price=special_price,
                                                                                offer=offer)

                for f in request.FILES.getlist('product_img'):
                    ProductImageByColour.objects.create(product_colour_id=prod_col_obj, image=f)

                prod_col_obj.size_and_qty.add(*size_list)

                prod_obj.available_colours.add(prod_col_obj)

                if prod_obj.min_price > int(special_price):
                    prod_obj.min_price = special_price
                    prod_obj.offer_of_min = offer

                if prod_obj.min_price == 0:
                    prod_obj.min_price = special_price
                    prod_obj.offer_of_min = offer

                prod_obj.is_row = False
                prod_obj.stock_status = True

                prod_obj.total_quantity = prod_obj.total_quantity + sum_of_qty(data.getlist('qty'))

                prod_obj.save()
                # add 3d images
                if request.FILES.get('back3d') and request.FILES.get('front3d'):
                    ProductImageFor3DView.objects.create(product=prod_obj, front=request.FILES.get('front3d'),
                                                         back=request.FILES.get('back3d'), colour=prod_col_obj,
                                                         wearable_type=data.get('cloths-type'))

                if data.get('click') == '2':

                    context = {
                        'colours': Colour.objects.all().exclude(
                            id__in=prod_obj.available_colours.all().values('colour'))
                    }
                    messages.success(request, 'Added successfully. Please add other Product Variants')

                    return HttpResponseRedirect('/admin/users/add_product_varients/' + str(product_id))
                else:
                    section_id = request.GET.get('section_id')
                    if section_id != '' and section_id != None:
                        backurl = '/admin/users/collection/'
                    else:
                        backurl = '/admin/users/product_list/'
                    return HttpResponseRedirect(backurl)

        context = {
            'form': form,
            'price': data['price'],
            'product_id': self.kwargs.get('product_id'),
            'special_price': data['special_price'],
            'colours': Colour.objects.all().exclude(
                id__in=prod_obj.available_colours.filter(is_active=True).values('colour'))
        }
        return render(request, 'admin-interface/product_management/add_sub_product.html', context)


class StylistDesignerViewProductView(View):
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs.get('product_id'))
        context = {
            'product': product
        }
        return render(request, 'admin-interface/product_management/view_product_main.html', context)


class StylistDesignerViewProductVarientsView(View):
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs.get('product_id'))

        available_colours_list = product.available_colours.filter(is_active=True)
        for available_colours in available_colours_list:
            available_colours.images = ProductImageByColour.objects.filter(product_colour_id=available_colours.id)

        context = {
            'available_colours': available_colours_list,
            'product_id': self.kwargs.get('product_id'),
            'product_name': product.name
        }
        return render(request, 'admin-interface/product_management/view_product_varients.html', context)


class StylistDesignerProductDatefilter(View):
    def get(self, request, *args, **kwargs):
        role = self.kwargs['role']
        print(request.GET)
        user = request.user

        start_date = datetime.datetime.strptime(request.GET.get('startdate'), '%m/%d/%Y').strftime('%Y-%m-%d')

        end_date = datetime.datetime.strptime(request.GET.get('enddate'), '%m/%d/%Y').strftime('%Y-%m-%d')

        category = Category.objects.all()
        products = Product.objects.filter(user=user, is_deleted=False,
                                          created_date__range=(start_date, end_date)).select_related('usercategory')
        context = {
            'products': products,
            'categories': category

        }

        return render(request, 'admin-interface/product_management/product_list.html', context)


class StylistDesignerProductEditView(View):

    def get(self, request, *args, **kwargs):
        product_id = self.kwargs['product_id']
        product = Product.objects.select_related('category', 'subcategory', 'subsubcategory', 'usercategory').get(
            pk=product_id)
        print(product)

        allcategory = Category.objects.filter(active=True)

        allsubcategory = SubCategory.objects.filter(category=product.category, active=True)
        allsubsubcategory = SubSubCategory.objects.filter(subcategory=product.subcategory, active=True)
        allowncategory = DSCategory.objects.filter(user=request.user)

        section_id = request.GET.get('section_id')
        if section_id != '' and section_id != None:
            backurl = '/admin/users/collection/'
        else:
            backurl = '/admin/users/product_list/'

        context = {
            'product': product,
            'categories': allcategory,
            'subcategories': allsubcategory,
            'subsubcategories': allsubsubcategory,
            'owncategories': allowncategory,
            'backurl': backurl

        }

        return render(request, 'admin-interface/product_management/edit_product_main_info.html', context)

    def post(self, request, *args, **kwargs):

        data = request.POST
        form = ProductCreateForm(request.POST or None)
        product_id = self.kwargs['product_id']
        print(form.is_valid())
        print(request.POST)
        if form.is_valid():

            product = Product.objects.select_related('category', 'subcategory', 'subsubcategory', 'usercategory').get(
                pk=product_id)

            category = Category.objects.get(pk=data['category'])
            subcategory = SubCategory.objects.get(pk=data['subcategory'])
            subsubcategory = SubSubCategory.objects.get(pk=data['subsubcategory'])

            product.name = data['name']
            product.category = category
            product.subcategory = subcategory
            product.subsubcategory = subsubcategory

            if data.get('owncategory') != '' and data.get('owncategory') != None:
                owncategory = DSCategory.objects.get(pk=data.get('owncategory'))
            else:
                owncategory = None

            if form.cleaned_data.get('new_from') != '' and form.cleaned_data.get('new_to') != '':
                new_from = datetime.datetime.strptime(form.cleaned_data.get('new_from'), '%m/%d/%Y').strftime(
                    '%Y-%m-%d')
                new_to = datetime.datetime.strptime(form.cleaned_data.get('new_to'), '%m/%d/%Y').strftime('%Y-%m-%d')
            else:
                new_from = None
                new_to = None

            product.usercategory = owncategory
            product.description = data['des']
            product.fit = data['fit']
            product.material = data['material']
            product.pattern = data['pattern']
            product.more_info = data['more_info']
            product.special_price = data.get('offer_price')
            product.new_from = new_from
            product.new_to = new_to
            product.brand = data['brand']
            # product.active = data['is_active']

            if request.FILES.get('main_img') is not None:
                product.main_img = request.FILES['main_img']

            product.save()

            section_id = request.GET.get('section_id')
            if section_id != '' and section_id != None:
                return HttpResponseRedirect('/admin/users/collection/')

            messages.success(request, 'Your product has been updated successfully')

            return HttpResponseRedirect('/admin/users/edit_product/' + str(product_id))

        product = Product.objects.select_related('category', 'subcategory', 'subsubcategory', 'usercategory').get(
            pk=product_id)
        print(product)

        allcategory = Category.objects.filter(active=True)

        allsubcategory = SubCategory.objects.filter(category=product.category, active=True)
        allsubsubcategory = SubSubCategory.objects.filter(subcategory=product.subcategory, active=True)
        allowncategory = DSCategory.objects.filter(user=request.user)

        section_id = request.GET.get('section_id')
        if section_id != '' and section_id != None:
            backurl = '/admin/users/collection/'
        else:
            backurl = '/admin/users/product_list/'

        context = {
            'product': product,
            'categories': allcategory,
            'subcategories': allsubcategory,
            'subsubcategories': allsubsubcategory,
            'owncategories': allowncategory,
            'backurl': backurl,

        }

        return render(request, 'admin-interface/product_management/editproduct.html', context)


class StylistDesignerProductVarientEditView(View):
    def get(self, request, *args, **kwargs):
        varient = get_object_or_404(ProductAvailableColourWithSizeQty, pk=self.kwargs.get('varient_id'))
        prod_obj = Product.objects.get(id=self.kwargs.get('product_id'))
        varient.images = ProductImageByColour.objects.filter(product_colour_id=self.kwargs.get('varient_id'))
        d_images_qs = ProductImageFor3DView.objects.filter(product=prod_obj, colour_id=varient)

        if d_images_qs.exists():
            d_images_obj = d_images_qs.first()
        else:
            d_images_obj = ProductImageFor3DView.objects.none()

        context = {
            'available_colours': varient,
            'product_id': self.kwargs.get('product_id'),
            'colours': Colour.objects.all().exclude(id__in=prod_obj.available_colours.filter(is_active=True).exclude(
                id=self.kwargs.get('varient_id')).values('colour')),
            'size_list': list(varient.size_and_qty.all().values_list('id', flat=True)),
            '3d_images': d_images_obj
        }

        return render(request, 'admin-interface/product_management/edit_product_varients.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        product_id = self.kwargs.get('product_id')
        print(data)
        form = AddProductVarientsForm(data or None)

        if len(data.getlist('size')) != len(set(data.getlist('size'))):
            form.add_error(None, "You can not select same size more than one")
        prod_obj = Product.objects.prefetch_related('available_colours').get(id=product_id)

        if request.FILES.getlist('product_img') == [] and not ProductImageByColour.objects.filter(
                product_colour_id=self.kwargs.get('varient_id')).exists():
            form.add_error(None, "Please select some product images")
        if data.getlist('size') == [] or data.getlist('size') == None:
            form.add_error(None, "Please select size and quantity of product variant")

        if form.is_valid():

            if prod_obj:

                actual_price = data['price']

                special_price = data.get('special_price')

                if special_price == '':
                    special_price = actual_price
                    offer = 0
                else:
                    offer = ((int(data['price']) - int(special_price)) * 100 // int(data['price']))

                prod_col_obj = ProductAvailableColourWithSizeQty.objects.prefetch_related('size_and_qty').get(
                    id=self.kwargs.get('varient_id'))

                qs = ProductSizeWithQty.objects.filter(id__in=prod_col_obj.size_and_qty.all())
                previous_qty = qs.aggregate(Sum('available_qty'))
                qs.delete()

                size_list = []
                for i in range(len(data.getlist('qty'))):
                    size = data.getlist('size')[i]
                    qty = data.getlist('qty')[i]

                    if size == 'XS':
                        sort_id = 1
                    elif size == 'S':
                        sort_id = 2
                    elif size == 'M':
                        sort_id = 3
                    elif size == 'L':
                        sort_id = 4
                    elif size == 'XL':
                        sort_id = 5
                    elif size == 'XXL':
                        sort_id = 6
                    elif size == 'XXXL':
                        sort_id = 7

                    obj = ProductSizeWithQty.objects.create(size=size, initial_qty=qty, available_qty=qty,
                                                            sort_id=sort_id)
                    size_list.append(obj)

                print(data['price'], data['special_price'], offer)
                colour = Colour.objects.get(id=data['colour'])
                prod_col_obj.colour = colour
                prod_col_obj.actual_price = data['price']
                prod_col_obj.special_price = special_price
                prod_col_obj.offer = offer

                total_quantity = sum_of_qty(data.getlist('qty'))
                if total_quantity > 0:
                    prod_col_obj.is_out_of_stock = False
                prod_col_obj.save()

                if request.FILES.getlist('product_img') != []:
                    for f in request.FILES.getlist('product_img'):
                        ProductImageByColour.objects.create(product_colour_id=prod_col_obj, image=f)

                dview_qs = ProductImageFor3DView.objects.filter(product=prod_obj, colour=prod_col_obj)

                if dview_qs.exists():
                    # update
                    dview_obj = dview_qs.first()
                    if request.FILES.get('front3d'):
                        dview_obj.front = request.FILES.get('front3d')
                    if request.FILES.get('back3d'):
                        dview_obj.back = request.FILES.get('back3d')

                    dview_obj.wearable_type = data.get('cloths-type')
                    dview_obj.save()
                else:
                    # create new one
                    if request.FILES.get('back3d') and request.FILES.get('front3d'):
                        ProductImageFor3DView.objects.create(product=prod_obj, front=request.FILES.get('front3d'),
                                                             back=request.FILES.get('back3d'), colour=prod_col_obj,
                                                             wearable_type=data.get('cloths-type'))
                # prod_obj.is_3d_view_available = True

                prod_col_obj.size_and_qty.add(*size_list)

                min_price_varient = prod_obj.available_colours.filter(is_active=True).order_by('special_price')[0]

                prod_obj.min_price = min_price_varient.special_price

                prod_obj.offer_of_min = min_price_varient.offer

                prod_obj.total_quantity = abs(
                    prod_obj.total_quantity - previous_qty['available_qty__sum'] + total_quantity)

                if total_quantity > 0:
                    prod_obj.stock_status = True

                prod_obj.save()

                if data.get('click') == '1':
                    return HttpResponseRedirect('/admin/users/view_product_varients/' + str(product_id))
                else:
                    section_id = request.GET.get('section_id')
                    if section_id != '' and section_id != None:
                        backurl = '/admin/users/collection/'
                    else:
                        backurl = '/admin/users/product_list/'
                    return HttpResponseRedirect(backurl)

        varient = get_object_or_404(ProductAvailableColourWithSizeQty, pk=self.kwargs.get('varient_id'))
        prod_obj = Product.objects.get(id=self.kwargs.get('product_id'))
        varient.images = ProductImageByColour.objects.filter(product_colour_id=self.kwargs.get('varient_id'))
        d_images_qs = ProductImageFor3DView.objects.filter(product=prod_obj, colour_id=varient)

        if d_images_qs.exists():
            d_images_obj = d_images_qs.first()
        else:
            d_images_obj = ProductImageFor3DView.objects.none()

        context = {
            'form': form,
            'available_colours': varient,
            'colours': Colour.objects.all().exclude(
                id__in=prod_obj.available_colours.all().exclude(id=self.kwargs.get('varient_id')).values('colour')),
            'size_list': list(varient.size_and_qty.all().values_list('id', flat=True)),
            '3d_images': d_images_obj
        }

        return render(request, 'admin-interface/product_management/edit_product_varients.html', context)


class ProductSearchByCatSubAndSubSubView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/admin/users/product_list/3')

    def post(self, request, *args, **kwargs):
        if request.POST['category'] and request.POST['subcategory'] and request.POST['subsubcategory'] is not None:
            user = request.user
            category = Category.objects.all()
            products = Product.objects.filter(user=user, category=request.POST['category'],
                                              subcategory=request.POST['subcategory'],
                                              subsubcategory=request.POST['subsubcategory'], is_deleted=False)

            context = {
                'products': products,
                'categories': category

            }
            return render(request, 'admin-interface/product_management/product_list.html', context)


class CouponView(View):

    def get(self, request, *args, **kwargs):
        qs = CouponCode.objects.all()
        context = {
            'coupons': qs,
        }
        return render(request, 'admin-interface/offer_management/coupon.html', context)


class AddCouponView(View):

    def get(self, request, *args, **kwargs):
        users = UserOtherInfo.objects.all().select_related('user')
        products = Product.objects.filter(is_deleted=False).values('name', 'id', 'active', 'created_date')

        context = {
            'users': users,
            'products': products

        }
        return render(request, 'admin-interface/offer_management/add_coupon.html', context)

    def post(self, request, *args, **kwargs):

        data = request.POST

        form = CouponAddForm(request.POST or None)

        print(form.is_valid())

        print(data)

        if data.get('coupon_type') == '1':
            if int(data.get('value')) > 100:
                form.add_error(None, "Percent value can't be greater than 100")

        if data.get('is_all_user') is None and data.get('selectedUserIds') is None:
            form.add_error(None, "Please select eligible users for coupon")

        if data.get('is_all_product') is None and data.get('selectedProductIds') is None:
            form.add_error(None, "Please select eligible products for coupon")

        qs = CouponCode.objects.filter(code=data.get('code'))
        if qs.exists():
            form.add_error(None, 'Coupon code with name ' + '(' + data.get(
                'code') + ')' + ' already exist.Please try with other')

        if form.is_valid():

            valid_to = datetime.datetime.strptime(form.cleaned_data.get('valid_to'), '%m/%d/%Y').strftime('%Y-%m-%d')
            valid_from = datetime.datetime.strptime(form.cleaned_data.get('valid_from'), '%m/%d/%Y').strftime(
                '%Y-%m-%d')

            obj = CouponCode.objects.create(code=request.POST['code'].upper(), coupon_type=request.POST['coupon_type'],
                                            value=request.POST['value'], max_amount=request.POST.get('max_amount'),
                                            usage_limit=request.POST['usage_limit'], valid_to=valid_to,
                                            valid_from=valid_from, terms_and_cond=request.POST['terms'],
                                            description=request.POST['description'],
                                            is_for_all_user=request.POST['is_all_user'],
                                            is_for_all_product=request.POST['is_all_product'])

            if data.getlist('selectedUserIds') is not None and request.POST.get('is_all_user') == 'False':
                obj.selected_users.add(*data.getlist('selectedUserIds'))

            if data.getlist('selectedProductIds') is not None and request.POST.get('is_all_user') == 'False':
                obj.selected_product.add(*data.getlist('selectedProductIds'))

            # messages.success(request, 'Coupon added successfully')

            return HttpResponseRedirect('/admin/users/coupon_management/')

        users = UserOtherInfo.objects.all().select_related('user')
        products = Product.objects.filter(is_deleted=False).values('name', 'id', 'active', 'created_date')

        context = {

            'form': form,
            'users': users,
            'products': products,
            'code': data.get('code'),
            'value': data.get('value'),
            'terms': data.get('terms'),
            'description': data.get('description'),
            'startdate': data.get('valid_from'),
            'enddate': data.get('valid_to'),

        }

        return render(request, 'admin-interface/offer_management/add_coupon.html', context)


class DeliveryChargesView(View):

    def get(self, request, *args, **kwargs):
        delivery_charges = DeliveryDistanceManagement.objects.all()

        context = {
            'delivery_charges': delivery_charges
        }

        return render(request, 'admin-interface/delivery_management/delivery_charges.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        form = DeliveryChargesAddForm(request.POST or None)

        if form.is_valid():
            DeliveryDistanceManagement.objects.create(dist_from=data['dist_from'],
                                                      dist_to=data['dist_to'], charges=data['charge'], )

            messages.success(request, 'added successfully')

            return HttpResponseRedirect('/admin/users/delivery_charges/')

        delivery_charges = DeliveryDistanceManagement.objects.all()

        context = {
            'form': form,
            'delivery_charges': delivery_charges,
            'dist_from': data.get('dist_from'),
            'dist_to': data.get('dist_to'),
            'charge': data.get('charge'),
        }

        return render(request, 'admin-interface/delivery_management/delivery_charges.html', context)


class EditDeliveryCharges(View):

    def get(self, request, *args, **kwargs):
        delivery_charge = DeliveryDistanceManagement.objects.get(id=request.GET.get('id'))
        print(delivery_charge)
        context = {

            'dist_to': delivery_charge.dist_to,
            'dist_from': delivery_charge.dist_from,
            'charge': delivery_charge.charges,
            'id': delivery_charge.id

        }

        return render(request, 'admin-interface/delivery_management/edit_delivery_charges.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        form = DeliveryChargesForm(data or None, id=data.get('id'))

        if form.is_valid():
            obj = DeliveryDistanceManagement.objects.get(id=data.get('id'))
            obj.dist_from = data.get('dist_from')
            obj.dist_to = data.get('dist_to')
            obj.charges = data.get('charge')
            obj.save()

            return HttpResponseRedirect('/admin/users/delivery_charges/')

        # delivery_charge = DeliveryDistanceManagement.objects.get(id= data.get('id'))
        context = {
            'form': form,
            'dist_from': data.get('dist_from'),
            'dist_to': data.get('dist_to'),
            'id': data.get('id'),
            'charge': data.get('charge'),

        }

        return render(request, 'admin-interface/delivery_management/edit_delivery_charges.html', context)


class EditCouponView(View):

    def get(self, request, *args, **kwargs):
        coupon = CouponCode.objects.prefetch_related('selected_users', 'selected_product').get(
            id=self.kwargs.get('coupon_id'))

        users = UserOtherInfo.objects.all().select_related('user').exclude(user_id__in=coupon.selected_users.all())
        selected_users = UserOtherInfo.objects.filter(user_id__in=coupon.selected_users.all())

        products = Product.objects.filter(is_deleted=False).values('name', 'id', 'active', 'created_date').exclude(
            id__in=coupon.selected_product.all())
        selected_product = Product.objects.filter(id__in=coupon.selected_product.all())

        context = {
            'coupon': coupon,
            'users': users,
            'selected_users': selected_users,
            'selected_products': selected_product,
            'products': products,

        }
        return render(request, 'admin-interface/offer_management/edit_coupon.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)

        form = CouponAddForm(data or None)

        if data.get('coupon_type') == '1':
            if int(data.get('value')) > 100:
                form.add_error(None, "Percent value can't be greater than 100")

        if data.get('is_all_user') is None and data.get('selectedUserIds') is None:
            form.add_error(None, "Please select eligible users for coupon")

        if data.get('is_all_product') is None and data.get('selectedProductIds') is None:
            form.add_error(None, "Please select eligible products for coupon")

        qs = CouponCode.objects.filter(code=data.get('code')).exclude(id=self.kwargs.get('coupon_id'))
        if qs.exists():
            form.add_error(None, 'Coupon code with name ' + '(' + data.get(
                'code') + ')' + ' already exist.Please try with other')

        if form.is_valid():
            obj = CouponCode.objects.get(id=self.kwargs.get('coupon_id'))

            valid_to = datetime.datetime.strptime(form.cleaned_data.get('valid_to'), '%m/%d/%Y').strftime('%Y-%m-%d')
            valid_from = datetime.datetime.strptime(form.cleaned_data.get('valid_from'), '%m/%d/%Y').strftime(
                '%Y-%m-%d')

            if request.POST.get('is_all_user') == 'True':
                print('yes')
                obj.selected_users.remove(*obj.selected_users.all())

            if request.POST.get('is_all_product') == 'True':
                print('yes')
                obj.selected_product.remove(*obj.selected_product.all())

            obj.code = request.POST['code'].upper()
            obj.coupon_type = request.POST['coupon_type']
            obj.value = request.POST['value']
            obj.max_amount = request.POST.get('max_amount')
            obj.usage_limit = request.POST['usage_limit']
            obj.valid_to = valid_to
            obj.valid_from = valid_from
            obj.terms_and_cond = request.POST['terms']
            obj.description = request.POST['description']
            obj.is_for_all_user = request.POST.get('is_all_user')
            obj.is_for_all_product = request.POST.get('is_all_product')

            obj.save()

            if data.getlist('selectedUserIds') is not None and request.POST.get('is_all_user') == 'False':
                obj.selected_users.remove(*obj.selected_users.all())
                obj.selected_users.add(*data.getlist('selectedUserIds'))

            if data.getlist('selectedProductIds') is not None and request.POST.get('is_all_product') == 'False':
                obj.selected_product.remove(*obj.selected_product.all())
                obj.selected_product.add(*data.getlist('selectedProductIds'))

            # messages.success(request, 'coupon edited successfully')

            # return HttpResponseRedirect('/admin/users/coupon_edit/' + str(self.kwargs.get('coupon_id')))
            return HttpResponseRedirect('/admin/users/coupon_management/')

        coupon = CouponCode.objects.prefetch_related('selected_users', 'selected_product').get(
            id=self.kwargs.get('coupon_id'))

        users = UserOtherInfo.objects.all().select_related('user').exclude(user_id__in=coupon.selected_users.all())
        selected_users = UserOtherInfo.objects.filter(user_id__in=coupon.selected_users.all())

        products = Product.objects.filter(is_deleted=False).values('name', 'id', 'active', 'created_date').exclude(
            id__in=coupon.selected_product.all())
        selected_product = Product.objects.filter(id__in=coupon.selected_product.all())

        context = {
            'form': form,
            'coupon': coupon,
            'users': users,
            'selected_users': selected_users,
            'selected_products': selected_product,
            'products': products,

        }

        return render(request, 'admin-interface/offer_management/edit_coupon.html', context)


class ReturnAndRefundPolicy(View):

    def get(self, request):

        obj = ReturnAndRefundPloicy.objects.all().first()

        if obj:
            return_policy = obj.return_policy
            refund_policy = obj.refund_policy
            id = obj.id
        else:
            refund_policy = ''
            return_policy = ''
            id = None

        context = {
            'return_policy': return_policy,
            'refund_policy': refund_policy,
            'id': id,
        }

        return render(request, 'admin-interface/return_refund_policy/return_refund_policy.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        form = ReturnAndRefundPolicyForm(data or None)
        if form.is_valid():

            if data['id'] == 'None':

                ReturnAndRefundPloicy.objects.create(return_policy=form.cleaned_data['return_policy'],
                                                     refund_policy=form.cleaned_data['refund_policy'])
                messages.success(request, 'Created successfully')

            else:
                obj = ReturnAndRefundPloicy.objects.get(id=int(data['id']))
                obj.return_policy = form.cleaned_data['return_policy']
                obj.refund_policy = form.cleaned_data['refund_policy']
                obj.save()
                messages.success(request, 'Updated successfully')

            return HttpResponseRedirect('/admin/users/return_and_refund_policy/')

        context = {
            'form': form,
            'return_policy': request.POST['return_policy'],
            'refund_policy': request.POST['refund_policy'],
            'id': data.get('id'),
        }

        return render(request, 'admin-interface/return_refund_policy/return_refund_policy.html', context)


class TermsAboutContactView(View):

    def get(self, request, *args, **kwargs):

        obj = ContactAboutTerms.objects.all().first()

        if obj:
            about_us = obj.about_us
            terms = obj.terms
            contact_us = obj.contact_us
            id = obj.id
        else:
            about_us = ''
            terms = ''
            contact_us = ''
            id = None

        context = {
            'about_us': about_us,
            'terms': terms,
            'contact_us': contact_us,
            'id': id
        }
        return render(request, 'admin-interface/settings_management/terms_about_contact.html', context)

    def post(self, request, *args, **kwargs):

        data = request.POST
        print(data)
        form = ContactAboutTermsForm(data or None)
        if form.is_valid():
            if data['id'] == 'None':

                ContactAboutTerms.objects.create(about_us=form.cleaned_data['about_us'],
                                                 terms=form.cleaned_data['terms'],
                                                 contact_us=form.cleaned_data['contact_us'])
                messages.success(request, 'Created successfully')

            else:
                obj = ContactAboutTerms.objects.get(id=int(data['id']))
                obj.about_us = form.cleaned_data['about_us']
                obj.terms = form.cleaned_data['terms']
                obj.contact_us = form.cleaned_data['contact_us']
                obj.save()
                messages.success(request, 'Updated successfully')

            return HttpResponseRedirect('/admin/users/terms_about_contact/')

        context = {
            'form': form,
            'about_us': data['about_us'],
            'terms': data['terms'],
            'contact_us': data['contact_us'],
            'id': data.get('id'),

        }

        return render(request, 'admin-interface/settings_management/terms_about_contact.html', context)


class FAQView(View):

    def get(self, request, *args, **kwargs):
        faq_qs = Faq.objects.all()
        context = {
            'faqs': faq_qs
        }
        return render(request, 'admin-interface/settings_management/faq.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        form = FaqForm(request.POST or None)
        if form.is_valid():
            if data['id'] == 'None' or data['id'] == '':

                Faq.objects.create(query=form.cleaned_data['query'],
                                   answer=form.cleaned_data['answer'])
                messages.success(request, 'Created successfully')

            else:
                obj = Faq.objects.get(id=int(data['id']))
                obj.query = form.cleaned_data['query']
                obj.answer = form.cleaned_data['answer']
                obj.save()
                messages.success(request, 'Updated successfully')

            return HttpResponseRedirect('/admin/users/faq/')

        context = {
            'form': form,
            'about_us': data['query'],
            'terms': data['answer'],
            'id': data.get('id'),

        }

        return render(request, 'admin-interface/settings_management/faq.html', context)


class TMCView(View):
    def get(self, request):
        data = ContactAboutTerms.objects.values('terms').all().first()
        return render(request, 'app_web_pages/tmc.html', context={'data': data})


class AboutUsView(View):
    def get(self, request):
        data = ContactAboutTerms.objects.values('about_us').all().first()
        return render(request, 'app_web_pages/about_us.html', context={'data': data})


class ContactUsView(View):
    def get(self, request):
        data = ContactAboutTerms.objects.values('contact_us').all().first()
        return render(request, 'app_web_pages/contact_us.html', context={'data': data})


class FAQWebView(View):
    def get(self, request):
        # data = ContactAboutTerms.objects.values('contact_us').all().first()
        faqs = Faq.objects.all()
        return render(request, 'app_web_pages/faq.html', context={'faqs': faqs})


from django.db.models import Q


class AddAudiVideoChargesView(View):
    def get(self, request):
        charges = AudioVideoCharges.objects.filter(user__role__role_id__in=["3", "4"]).select_related('user')
        users = UserOtherInfo.objects.filter(role__role_id__in=["3", "4"]).filter(
            ~Q(id__in=charges.values_list('user__id'))).select_related('user')
        return render(request, 'admin-interface/audio_video_charges_management/add_charges.html',
                      context={'charges': charges, 'users': users})

    def post(self, request):
        data = request.POST
        form = AudioVideoChargesForm(request.POST or None)
        users_list = data.getlist('selectedUserIds')

        if users_list is None or users_list == []:
            form.add_error(None, "Please select at least one stylist/designer")
        if form.is_valid():

            audio_charge = form.cleaned_data['audio_charge']
            video_charge = form.cleaned_data['video_charge']

            # check already exist or not

            qs = AudioVideoCharges.objects.filter(user_id__in=users_list)
            if qs.exists() and qs.count() == 1:
                charge_obj = qs.first()
                charge_obj.audio_charge = audio_charge
                charge_obj.video_charge = video_charge
                charge_obj.save()
                messages.success(request, 'updated successfully')
                return HttpResponseRedirect('/admin/users/audio_video_charges')

            # make object from bulk create

            user_objs = [AudioVideoCharges(audio_charge=audio_charge, video_charge=video_charge, user_id=user) for user
                         in users_list]

            AudioVideoCharges.objects.bulk_create(user_objs)
            messages.success(request, 'added successfully')
            return HttpResponseRedirect('/admin/users/audio_video_charges')

        charges = AudioVideoCharges.objects.filter(user__role__role_id__in=["3", "4"]).select_related('user')
        users = UserOtherInfo.objects.filter(role__role_id__in=["3", "4"]).filter(
            ~Q(id__in=charges.values_list('user__id'))).select_related('user')
        context = {
            'form': form,
            'audio_charge': data['audio_charge'],
            'video_charge': data['audio_charge'],
            'charges': charges,
            'users': users

        }
        return render(request, 'admin-interface/audio_video_charges_management/add_charges.html', context)


from orders.models import OrderedProductStatus


class OrderView(View):
    @order_permission_required
    def get(self, request, *args, **kwargs):
        user = request.user
        startdate = request.GET.get('startdate')
        enddate = request.GET.get('enddate')
        if startdate is not None and enddate is not None:
            start_date = datetime.datetime.strptime(startdate, '%m/%d/%Y').strftime('%Y-%m-%d')

            end_date = datetime.datetime.strptime(enddate, '%m/%d/%Y').strftime('%Y-%m-%d')

        if user.is_authenticated:

            role = request.COOKIES['role']
            if role == '2':
                if startdate is not None and enddate is not None:
                    orders = OrderedProductStatus.objects.filter(created__range=(start_date, end_date)).order_by(
                        '-created')
                else:
                    orders = OrderedProductStatus.objects.all().order_by('-created')
            else:
                if startdate is not None and enddate is not None:
                    orders = OrderedProductStatus.objects.filter(created__range=(start_date, end_date),
                                                                 cart__product__user=user).select_related('order',
                                                                                                          'user').order_by(
                        '-created')
                else:
                    orders = OrderedProductStatus.objects.filter(cart__product__user=user).select_related('order',
                                                                                                          'user').order_by(
                        '-created')

            return render(request, 'admin-interface/order_management/order_list.html',
                          context={'orders': orders, 'status_id': '0', 'startdate': startdate, 'enddate': enddate})
        return render(request, 'admin-interface/order_management/order_list.html',
                      context={'orders': [], 'status_id': '0', 'startdate': startdate, 'enddate': enddate})

    def post(self, request, *args, **kwargs):
        user = request.user
        status_id = request.POST.get('status_id')

        if user.is_authenticated:

            role = request.COOKIES['role']
            if role == '2':
                if status_id == '0':
                    orders = OrderedProductStatus.objects.all().select_related('order', 'user', 'order__address',
                                                                               'cart__product').order_by('-created')
                else:
                    orders = OrderedProductStatus.objects.filter(order_status=status_id).select_related('order', 'user',
                                                                                                        'order__address',
                                                                                                        'cart__product').order_by(
                        '-created')
            else:
                if status_id == '0':
                    orders = OrderedProductStatus.objects.filter(cart__product__user=user).select_related('order',
                                                                                                          'user',
                                                                                                          'order__address',
                                                                                                          'cart__product').order_by(
                        '-created')
                else:
                    orders = OrderedProductStatus.objects.filter(order_status=status_id,
                                                                 cart__product__user=user).select_related('order',
                                                                                                          'user',
                                                                                                          'order__address',
                                                                                                          'cart__product').order_by(
                        '-created')
            return render(request, 'admin-interface/order_management/order_list.html',
                          context={'orders': orders, 'status_id': status_id})
        return render(request, 'admin-interface/order_management/order_list.html',
                      context={'orders': '', 'status_id': status_id})


from orders.models import OrderStatusChangeDate


class OrderDetailView(View):
    def get(self, request, *args, **kwargs):
        order_detail_id = self.kwargs.get('order_id')

        try:
            order_obj = OrderedProductStatus.objects.get(id=order_detail_id)
            if order_obj.order_status != '1':
                order_status_detail = OrderStatusChangeDate.objects.filter(order=order_obj,
                                                                           order_status=order_obj.order_status).first()

            else:
                order_status_detail = None
        except:
            return render(request, 'admin-interface/order_management/order_detail.html')

        context = {
            'order': order_obj,
            'order_status_detail': order_status_detail
        }
        return render(request, 'admin-interface/order_management/order_detail.html', context)


from django.core import mail
from django.template.loader import render_to_string

from payments.models import PaymentHistory, MemberPaymentHistory


class AddTrackingIdView(View):

    def post(self, request, *args, **kwargs):
        data = request.POST
        order_detail_id = self.kwargs.get('order_id')
        user = request.user

        try:
            order_obj = OrderedProductStatus.objects.get(id=order_detail_id)
            order_obj.track_id = data.get('id')
            order_obj.track_url = data.get('url')
            order_obj.order_status = '3'
            order_obj.save()
            OrderStatusChangeDate.objects.create(status_change_by=user, order=order_obj, order_status='3')

            ## send mail to user

            to = order_obj.user.email
            plain_message = None
            from_email = 'Viewed <webmaster@localhost>'
            subject = 'Product shipped successfully'
            message_text = render_to_string('mails/send_tracking_detail.html', {
                'user': user,
                'track_id': data.get('id'),
                'track_url': data.get('url'),
                'product': order_obj.cart.product.name,

            })
            mail.send_mail(subject, plain_message, from_email, [to], html_message=message_text)

            messages.success(request, 'Status changed and details sent to user by mail successfully.')

            return HttpResponseRedirect('/admin/users/order_detail/' + str(order_detail_id))
        except:

            messages.error(request, 'Something went wrong')
            return HttpResponseRedirect('/admin/users/order_detail/' + str(order_detail_id))


class PaymentListMemberTransView(View):
    @payment_permission_required
    def get(self, request, *args, **kwargs):

        user = request.user

        startdate = request.GET.get('startdate')
        enddate = request.GET.get('enddate')
        if startdate is not None and enddate is not None:
            start_date = datetime.datetime.strptime(startdate, '%m/%d/%Y').strftime('%Y-%m-%d')
            end_date = datetime.datetime.strptime(enddate, '%m/%d/%Y').strftime('%Y-%m-%d')

        if user.is_authenticated:

            role = request.COOKIES['role']
            if role == '2':
                if startdate is not None and enddate is not None:
                    orders = OrderedProductStatus.objects.filter(order_status='4',
                                                                 created__range=(start_date, end_date)).order_by(
                        '-created')
                    for order in orders:
                        order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()
                else:
                    orders = OrderedProductStatus.objects.filter(order_status='4').select_related('order',
                                                                                                  'user').order_by(
                        '-created')
                    for order in orders:
                        order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()

                return render(request, 'admin-interface/payment_management/member_transaction_list.html',
                              context={'orders': orders, 'sort_id': '1', 'startdate': startdate, 'enddate': enddate})
            else:
                if startdate is not None and enddate is not None:
                    orders = OrderedProductStatus.objects.filter(order_status='4', cart__product__user=request.user,
                                                                 created__range=(start_date, end_date)).order_by(
                        '-created')

                    for order in orders:
                        order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()
                else:
                    orders = OrderedProductStatus.objects.filter(order_status='4',
                                                                 cart__product__user=request.user, ).select_related(
                        'order', 'user').order_by('-created')
                    for order in orders:
                        order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()

                return render(request, 'admin-interface/payment_management/subadmin_member_transaction_list.html',
                              context={'orders': orders, 'sort_id': '1', 'startdate': startdate, 'enddate': enddate})
        return render(request, 'admin-interface/payment_management/member_transaction_list.html',
                      context={'orders': '', 'sort_id': '1', 'startdate': startdate, 'enddate': enddate})

    def post(self, request, *args, **kwargs):

        user = request.user
        sort_id = request.POST.get('sort_id')

        if user.is_authenticated:

            role = request.COOKIES['role']
            if role == '2':

                if sort_id == '1':
                    orders = OrderedProductStatus.objects.filter(order_status='4').order_by('-created')
                else:
                    orders = OrderedProductStatus.objects.filter(order_status='4',
                                                                 order__cart__product__user_role=sort_id).order_by(
                        '-created')

                for order in orders:
                    order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()

                return render(request, 'admin-interface/payment_management/member_transaction_list.html',
                              context={'orders': orders, 'sort_id': sort_id})
            else:
                orders = OrderedProductStatus.objects.filter(order_status='4',
                                                             created__range=(start_date, end_date)).order_by('-created')

                for order in orders:
                    order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()

                return render(request, 'admin-interface/payment_management/subadmin_member_transaction_list.html',
                              context={'orders': orders, 'sort_id': sort_id})
        return render(request, 'admin-interface/payment_management/member_transaction_list.html',
                      context={'orders': '', 'sort_id': sort_id})


class PaymentCustomerTransListView(View):
    @payment_permission_required
    def get(self, request, *args, **kwargs):

        user = request.user

        startdate = request.GET.get('startdate')
        enddate = request.GET.get('enddate')
        if startdate is not None and enddate is not None:
            start_date = datetime.datetime.strptime(startdate, '%m/%d/%Y').strftime('%Y-%m-%d')

            end_date = datetime.datetime.strptime(enddate, '%m/%d/%Y').strftime('%Y-%m-%d')

        if user.is_authenticated:

            role = request.COOKIES['role']
            if role == '2':
                if startdate is not None and enddate is not None:
                    orders = OrderedProductStatus.objects.filter(created__range=(start_date, end_date)).order_by(
                        '-created')
                    for order in orders:
                        order.payment = PaymentHistory.objects.filter(order_id=order.order).first()
                else:
                    orders = OrderedProductStatus.objects.all().select_related('order', 'user').order_by('-created')
                    for order in orders:
                        order.payment = PaymentHistory.objects.filter(order_id=order.order).first()

            return render(request, 'admin-interface/payment_management/customer_transaction_list.html',
                          context={'orders': orders, 'sort_id': '1', 'startdate': startdate, 'enddate': enddate})
        return render(request, 'admin-interface/payment_management/customer_transaction_list.html',
                      context={'orders': '', 'sort_id': '1', 'startdate': startdate, 'enddate': enddate})


# def post(self,request,*args,**kwargs):
# 	user = request.user
# 	sort_id = request.POST.get('sort_id')

# 	if user.is_authenticated:

# 		role = request.COOKIES['role']
# 		today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

# 		today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)

# 		# some_day_last_week = timezone.now().date() - timedelta(days=7)
# 		# monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
# 		# monday_of_this_week = monday_of_last_week + timedelta(days=7)

# 		if role=='2':
# 			if sort_id=='1':

# 				orders = OrderedProductStatus.objects.all().select_related('order','user').order_by('-created')
# 			else:
# 				orders = OrderedProductStatus.objects.filter(created__range=(start_date, end_date)).select_related('order','user').order_by('-created')

# 		return render(request, 'admin-interface/order_management/order_list.html', context={'orders':orders,'status_id':status_id})
# 	return render(request, 'admin-interface/order_management/order_list.html', context={'orders':orders,'status_id':status_id})


from django.db.models import Sum


class ReportGeneration(View):
    def get(self, request):

        user = request.user

        startdate = request.GET.get('startdate')
        enddate = request.GET.get('enddate')
        if startdate is not None and enddate is not None:
            start_date = datetime.datetime.strptime(startdate, '%m/%d/%Y').strftime('%Y-%m-%d')
            end_date = datetime.datetime.strptime(enddate, '%m/%d/%Y').strftime('%Y-%m-%d')

        if user.is_authenticated:
            role = request.COOKIES['role']
            if role == '2':
                if startdate is not None and enddate is not None:
                    orders = OrderedProductStatus.objects.filter(order_status='4',
                                                                 created__range=(start_date, end_date)).order_by(
                        '-created')
                    total_profit = 0
                    for order in orders:
                        special_price = order.cart.selected_colour.special_price

                        profit = (special_price * 10) / 100
                        order.profit = profit
                        total_profit = round(total_profit + profit, 3)
                        order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()
                else:
                    orders = OrderedProductStatus.objects.filter(order_status='4').select_related('order',
                                                                                                  'user').order_by(
                        '-created')
                    total_profit = 0
                    for order in orders:
                        special_price = order.cart.selected_colour.special_price
                        profit = (special_price * 10) / 100
                        order.profit = profit
                        total_profit = round(total_profit + profit, 3)
                        order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()

                return render(request, 'admin-interface/report_management/report.html',
                              context={'orders': orders, 'total_profit': total_profit, 'sort_id': '1',
                                       'startdate': startdate, 'enddate': enddate})
            else:
                if startdate is not None and enddate is not None:
                    orders = OrderedProductStatus.objects.filter(order_status='4', cart__product__user=request.user,
                                                                 created__range=(start_date, end_date)).order_by(
                        '-created')
                    total_profit = 0
                    for order in orders:
                        special_price = order.cart.selected_colour.special_price
                        profit = (special_price * 90) / 100
                        order.profit = profit
                        total_profit = round(total_profit + profit, 3)
                        order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()
                else:
                    orders = OrderedProductStatus.objects.filter(order_status='4',
                                                                 cart__product__user=request.user).select_related(
                        'order', 'user').order_by('-created')
                    total_profit = 0
                    for order in orders:
                        special_price = order.cart.selected_colour.special_price
                        profit = (special_price * 90) / 100
                        order.profit = profit
                        total_profit = round(total_profit + profit, 3)
                        order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()

            return render(request, 'admin-interface/report_management/report.html',
                          context={'orders': orders, 'sort_id': '1', 'total_profit': total_profit,
                                   'startdate': startdate, 'enddate': enddate})

        return render(request, 'admin-interface/report_management/report.html',
                      context={'orders': [], 'sort_id': '1', 'startdate': startdate, 'enddate': enddate})

    def post(self, request, *args, **kwargs):

        user = request.user
        sort_id = request.POST.get('sort_id')

        if user.is_authenticated:

            role = request.COOKIES['role']
            if role == '2':

                if sort_id == '1':
                    orders = OrderedProductStatus.objects.filter(order_status='4').order_by('-created')
                else:
                    orders = OrderedProductStatus.objects.filter(order_status='4',
                                                                 order__cart__product__user_role=sort_id).order_by(
                        '-created')

                total_profit = 0
                for order in orders:
                    special_price = order.cart.selected_colour.special_price

                    profit = (special_price * 10) / 100
                    order.profit = profit
                    total_profit = round(total_profit + profit, 3)
                    order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()

                return render(request, 'admin-interface/report_management/report.html',
                              context={'orders': orders, 'total_profit': total_profit, 'sort_id': sort_id})
            else:

                orders = OrderedProductStatus.objects.filter(order_status='4', created__range=(start_date, end_date),
                                                             cart__product__user=request.user).order_by('-created')
                total_profit = 0
                for order in orders:
                    special_price = order.cart.selected_colour.special_price

                    profit = (special_price * 90) / 100
                    order.profit = profit
                    total_profit = round(total_profit + profit, 3)
                    order.payment = MemberPaymentHistory.objects.filter(sub_order_id=order).first()

                return render(request, 'admin-interface/report_management/report.html',
                              context={'orders': orders, 'total_profit': total_profit, 'sort_id': sort_id})
        return render(request, 'admin-interface/report_management/report.html',
                      context={'orders': [], 'sort_id': sort_id})


class GraphReportGeneration(View):
    @report_permission_required
    def get(self, request):
        return render(request, 'admin-interface/report_management/graphs_report.html', context={})


# chat app


import firebase_admin
from firebase_admin import db


class ChatDashboardView(View):
    @chat_permission_required
    def get(self, request):
        user = request.user

        try:
            user_other_info = UserOtherInfo.objects.get(user=user)
        except:
            return render(request, 'admin-interface/chat_management/no_user.html',
                          context={})
        print(type(user_other_info.role))
        if user_other_info.role.role_id == '2':  # super admin
            print('in super admin')
            return render(request, 'admin-interface/chat_management/admin_chat_dashboard.html',
                          context={'user': user, 'opp_user': ''})

        try:
            profile = Profile.objects.get(user=user)
        except:
            profile = Profile.objects.none()

        if profile:
            user_profile_img = profile.profileimg.url
        else:
            if user_other_info.profileimg:
                user_profile_img = user_other_info.profileimg.url
            else:
                user_profile_img = ""

        # for stylist designer
        # firebase_admin.get_app()
        # recent_msg_node = db.reference('conversation')
        # user_node = db.reference('users')
        # messages_node =db.reference('messages')
        # try:
        # 	recent_chat_list =  recent_msg_node.child('user_'+str(user.id)).get()
        # 	if recent_chat_list:
        # 		for key in recent_chat_list:
        # 			if key.split('_')[0] == str(user.id):
        # 				opp_id =key.split('_')[1]
        # 			else:
        # 				opp_id = key.split('_')[0]
        #
        # 			opp_user = user_node.child('user_'+opp_id)
        # 			if opp_user:
        # 				opp_user = opp_user.get()
        #
        # 			last_message = messages_node.child(key).child(recent_chat_list[key]['last_message_location'])
        # 			if last_message:
        # 				last_message = last_message.get()
        # 			recent_chat_list[key]['lastmessage']=last_message
        # 			recent_chat_list[key]['opp_user']= opp_user
        # 		recent_chat_list = list(recent_chat_list.values())
        # except Exception as e:
        # 	return "get_record failed. {}".format(e)

        user = {
            'id': user.id,
            'name': user.first_name + ' ' + user.last_name,
            'profile_image': user_profile_img,
            'role': user_other_info.role.role_id
        }

        return render(request, 'admin-interface/chat_management/stylist_designer_chat_dashboard.html',
                      context={'user': user, 'recent_user_list': []})


class ChatBoxView(View):

    def get(self, request):
        user = request.user
        opp_user_id = request.GET.get('opp_user')
        user_other_info = UserOtherInfo.objects.get(user=user)
        try:
            profile = Profile.objects.get(user=user)
        except:
            profile = Profile.objects.none()

        if profile:
            user_profile_img = profile.profileimg.url
        else:
            if user_other_info.profileimg:
                user_profile_img = user_other_info.profileimg.url
            else:
                user_profile_img = ""

        # get opp_user form firebase
        firebase_admin.get_app()
        user_node = db.reference('Users')
        try:
            opp_user = user_node.child('user_' + opp_user_id).get()
        except Exception as e:
            return "get_record failed. {}".format(e)
        if not opp_user:
            return render(request, 'admin-interface/chat_management/no_user.html', context={})
        # get all chats list
        msgs_node = db.reference('Messages/PrivateMessages')
        msg_node_id = min(str(user.id), opp_user_id) + '_' + max(str(user.id), opp_user_id)
        try:
            message_list = msgs_node.child(msg_node_id).get()
            if message_list:
                message_list = list(message_list.values())
        except Exception as e:
            return "get_record failed. {}".format(e)

        user = {
            'id': user.id,
            'name': user.first_name + user.last_name,
            'profile_image': user_profile_img,
            'role': user_other_info.role.role_id
        }
        response = render(request, 'admin-interface/chat_management/chat.html',
                          context={'user': user, 'message_list': message_list, 'opp_user': opp_user})
        response.set_cookie('user', user)
        # get opp user from firebase

        return response


class ChatDashboardTest(View):
    def get(self, request):
        return render(request, 'admin-interface/chat_management/chat_test.html')


# class AudioCallView(View):
#     def get(self, request):
#         return render(request, 'admin-interface/chat_management/audio_management.html')

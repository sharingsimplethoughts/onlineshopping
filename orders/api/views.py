from rest_framework.generics import (
		CreateAPIView,
		ListAPIView
	)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
	HTTP_200_OK,
	HTTP_400_BAD_REQUEST
	,HTTP_204_NO_CONTENT,
	HTTP_201_CREATED,
	HTTP_500_INTERNAL_SERVER_ERROR,
	HTTP_404_NOT_FOUND
	)

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
import django_filters
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication
from product.models import ProductImageByColour
from .serializers import *
from orders.models import *

from django.core import mail
from django.template.loader import render_to_string

import logging
logger = logging.getLogger('payments')

from product.models import CustomerProductCart,Product
class DeliveryAddressAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request,*args,**kwargs):
		user= request.user 
		qs = CustomerAddress.objects.filter(user=request.user, is_active=True)
		data  = DeliveryAddressViewSerializer(qs,many=True).data

		return Response({
			'delivery_addresses':data,
			'message':'success'

			}, status=HTTP_200_OK)

	def post(self,request,*args,**kwargs):
		data = request.data

		serializer = DeliveryAddressAddSerializer(data=data)

		if serializer.is_valid():
			serializer.validated_data['user']=request.user
			serializer.save()
			return Response({
				'message':'address added successfully'
				} ,200)


		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class ActionOnDeliveryAddressAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request,*args,**kwargs):
		addr_id = self.kwargs.get('addr_id')
		try:
			
			obj = CustomerAddress.objects.get(pk = addr_id, user=request.user, is_active=True)
		except:
			return Response({
					
					'message':'Invalid address id'

					}, status=HTTP_400_BAD_REQUEST)

		data  = DeliveryAddressViewSerializer(obj).data

		return Response({
					'delivery_address':data,
					'message':'success'

					}, status=HTTP_200_OK)


	def delete(self,request,*args,**kwargs):
		addr_id = self.kwargs.get('addr_id')
		try:
			# checking, is address with any order

			qs = CustomerOrders.objects.filter(address = addr_id)
			if qs.exists():
				obj = CustomerAddress.objects.get(pk = addr_id,user=request.user)
				obj.is_active=False
				obj.save()
			else:

				CustomerAddress.objects.get(pk = addr_id,user=request.user).delete()
		except:
			return Response({
					
					'message':'Invalid address id'

					}, status=HTTP_400_BAD_REQUEST)

		return Response({
					
					'message':'Address deleted successfully '

					}, status=HTTP_200_OK)

	def put(self,request,*args,**kwargs):
		addr_id = self.kwargs.get('addr_id')
		data = request.data
		try:
			obj = CustomerAddress.objects.get(pk = addr_id,user=request.user,is_active=True)
		except:
			return Response({
				'message':'No address found'
				},400)
		serializer = DeliveryAddressAddSerializer(data=data, instance = obj )

		if serializer.is_valid():
			serializer.validated_data['user']=request.user
			serializer.save()
			return Response({
				'message':'address updated successfully'
				} ,200)

		return Response(serializer.errors ,400)


from django.db.models import Sum

def make_order(self,request,*args,**kwargs):

	user = request.user
	data = request.data
	all_cart_item = dict(request.data).get('cart')

	serializer = MakeOrderAPIViewSerializer(data=data)
	if serializer.is_valid():
		serializer.validated_data['user']=request.user
		obj = serializer.save()
		
		cart_list = [ OrderedProductStatus(user=request.user,order_id = obj.id ,cart_id = cart_id) for cart_id in all_cart_item]     
		OrderedProductStatus.objects.bulk_create(cart_list)

		product_list = [_.cart.product for _ in cart_list]
		### remove from cart 

		cart_qs = CustomerProductCart.objects.filter(id__in = all_cart_item)
		cart_qs.update(is_ordered=True)
		
		# decrease product available stock quantity

		for cart_obj in cart_qs:
			size_qs 	= cart_obj.selected_colour.size_and_qty.filter(size = cart_obj.selected_size)
			size_obj 	= size_qs.first()
			size_obj.available_qty = size_obj.available_qty - cart_obj.selected_quantity
			product_obj = cart_obj.product
			if cart_obj.selected_colour.size_and_qty.aggregate(Sum('available_qty'))['available_qty__sum'] == 0 :
				colour_obj = cart_obj.selected_colour
				colour_obj.is_out_of_stock = True
				colour_obj.save()

				# min_price_obj = product_obj.available_colours.filter(is_active=True, is_out_of_stock=False).order_by('special_price')
				# if min_price_obj.exists():
				# 	product_obj.min_price = min_price_obj.special_price
				# 	product_obj.offer_of_min = min_price_obj.offer

			size_obj.save()

			if product_obj.total_quantity - cart_obj.selected_quantity == 0:
				product_obj.stock_status = False
				# product_obj.active = False
			product_obj.total_quantity = abs(product_obj.total_quantity - cart_obj.selected_quantity)
			product_obj.qty_sold = product_obj.qty_sold + cart_obj.selected_quantity
			product_obj.save()

		return {
				'message':'Order placed successfully',
				'product_list':product_list,
				'order_id':obj.id,
				'status':200
				}

	return {
				'message':serializer.errors,
				'status':400
				}


def place_exchange_order(self, request, *args, **kwargs):

	user = request.user
	data = request.data
	cart_id = data.get('cart_id')
	
	# place order 
	saved_amount = int(data.get('actual_price'))-int(data.get('special_price'))
	order_detail_id = data.get('order_detail_id')

	try:
		previouse_order_obj = OrderedProductStatus.objects.get(id = order_detail_id)
	except:
		return {
			'message':'Invalid order_detail_id',
			'order_id':'',
			'status':400
			}

	if data.get('is_payment_required')==True or data.get('is_payment_required')=='true':

		order_obj = CustomerOrders.objects.create(user=request.user , address_id= data.get('address'),
										payment=data.get('payment'),is_coupon_applied=False,
										item=1, coupon_code="",coupon_off=0, shipping_charges=0,
										grand_total=data.get('grand_total'), saved_amount=saved_amount, exchange_previous_order=previouse_order_obj, is_exchange=True,price=data.get('actual_price'))

		order_obj.cart.add(cart_id )
	if  data.get('is_refund_required')==True or data.get('is_refund_required')=='true':
		order_obj = CustomerOrders.objects.create(user=request.user, address_id = data.get('address'),
								payment="", is_coupon_applied=False,
								item=1, coupon_code="", coupon_off=0, shipping_charges=0,
								grand_total = -data.get('grand_total'), is_refund_required=True, saved_amount=saved_amount, exchange_previous_order=previouse_order_obj, is_exchange=True, price=data.get('actual_price'))
		order_obj.cart.add(cart_id)
		# save refund bank details


	if data.get('is_refund_required')==False or data.get('is_refund_required')=='false' and data.get('is_payment_required')==False or  data.get('is_payment_required')=='false':
		order_obj = CustomerOrders.objects.create(user=request.user , address_id= data.get('address'),
						payment=previouse_order_obj.order.payment, is_coupon_applied=False,
						item=1, coupon_code="",coupon_off=0, shipping_charges=0,
						grand_total= 0, is_exchange=True, is_refund_required=False, exchange_previous_order=previouse_order_obj,saved_amount=saved_amount, price=data.get('actual_price'))

		order_obj.cart.add(cart_id)

	#change status of previous order 

	previouse_order_obj.order_status = "10"
	previouse_order_obj.save()
	# save in individual staus of product
	order_status_qs = OrderedProductStatus.objects.create(user=request.user, order = order_obj, cart_id = cart_id)     

	# decrease product available stock quantity
	cart_obj = CustomerProductCart.objects.filter(id = cart_id).first()

	size_qs 	= cart_obj.selected_colour.size_and_qty.filter(size = cart_obj.selected_size)
	size_obj 	= size_qs.first()
	size_obj.available_qty = size_obj.available_qty - cart_obj.selected_quantity
	product_obj = cart_obj.product
	if cart_obj.selected_colour.size_and_qty.aggregate(Sum('available_qty'))['available_qty__sum'] == 0 :
		colour_obj = cart_obj.selected_colour
		colour_obj.is_out_of_stock = True
		colour_obj.save()

		# min_price_obj = product_obj.available_colours.filter(is_active=True, is_out_of_stock=False).order_by('special_price')
		# if min_price_obj.exists():
		# 	product_obj.min_price = min_price_obj.special_price
		# 	product_obj.offer_of_min = min_price_obj.offer

	size_obj.save()

	if product_obj.total_quantity - cart_obj.selected_quantity == 0:
		product_obj.stock_status = False
		# product_obj.active = False
	product_obj.total_quantity = abs(product_obj.total_quantity - cart_obj.selected_quantity)
	product_obj.qty_sold = product_obj.qty_sold + cart_obj.selected_quantity
	product_obj.save()

	return {
			'message':'Order placed successfully',
			'order_id':order_obj.id,
			'status':200
			}




class MakeOrderAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self,request,*args,**kwargs):
	
		user = request.user
		data = request.data
		print(data)

		serializer = MakeOrderAPIViewSerializer(data=data)
		if serializer.is_valid():
			serializer.validated_data['user']=request.user
			obj = serializer.save()

			## create individual product status

			cart_list = [ OrderedProductStatus(user=request.user,order_id = obj.id ,cart_id = cart_id) for cart_id in request.data.get('cart')]
			OrderedProductStatus.objects.bulk_create(cart_list)

			### remove from cart 

			cart_qs = CustomerProductCart.objects.filter(id__in = request.data.get('cart')).update(is_ordered=True)



			return Response({
					'message':'Order placed successfully'
					} ,200)

		return Response(serializer.errors ,400)


from product.api.serializers import CustomerCartAllProductListSerializer
from product.models import CustomerProductCart

class AllOrderProductHistoryAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]


	def get(self,request,*args,**kwargs):
		history = OrderedProductStatus.objects.filter(user=request.user, order_status__in=[4,5,6,7,8,9,10,11]).order_by('-created')
		print(history,'history')
		history_data = AllOrderProductHistorySerializer(history,many=True).data
		ongoing = OrderedProductStatus.objects.filter(user=request.user, order_status__in=[1,2,3]).order_by('-created')
		print(ongoing,'ongoing')
		ongoing_data = AllOrderProductHistorySerializer(ongoing,many=True).data
		return Response({
				'history':history_data,
				'ongoing':ongoing_data,

				'message':'success'
				} ,200)


class AllOrderProductHistoryWebAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request,*args,**kwargs):
		history = OrderedProductStatus.objects.filter(user=request.user).order_by('-created')
		history_data = AllOrderProductHistorySerializer(history,many=True).data
		return Response({
				'history':history_data,
				'message':'success'
				} ,200)



class OrderedProductHistoryAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request,*args,**kwargs):
		try:
			order_detail = OrderedProductStatus.objects.get(id = self.kwargs.get('id'), user = request.user )
		except:
			return Response({
					'message':'Invalid id'
					} ,400)

		order_detail_data = OrderdProductHistorySerializer(order_detail,context={'request':request}).data
		# edit for latest_status
		# if order_detail.order_status == '1':
		latest_status = {
			'created':(order_detail.created).strftime("%a, %b%d '%y"),
			'order_status':order_detail.order_status
		}
		# else:
		# 	latest_status = OrderStatusChangeDateSerializer(OrderStatusChangeDate.objects.filter(order__id=self.kwargs.get('id')).order_by('-created').first()).data
		return Response({
				'order_detail':order_detail_data,
				'latest_status':latest_status,
				'message':'success'
				} ,200)



class ProductRateAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data
		order_detail_id  = data.get('order_detail_id')
		rating = data.get('rating')
		if not (order_detail_id is None or  order_detail_id=='' or rating is None or rating==''):
			if int(rating) > 5:
				return Response({
					'message':'rating can not be greater than 5'
					},200)
			try:
				ord_obj = OrderedProductStatus.objects.get(id=order_detail_id )
			except:
				return Response({
					'message':'Invalid order_detail_id'
					},200)

			prod_obj = ord_obj.cart.product
			
			review_qs = OrderedProductReviews.objects.filter(user=request.user, order = ord_obj)
			if review_qs.exists():
				review_obj = review_qs.first()
				review_obj.rating = rating
				review_obj.save()

				# update avg_review
				review_count = OrderedProductReviews.objects.filter(product=prod_obj).count()
				cal_rating = ((prod_obj.avg_rating*review_count) + int(rating)-prod_obj.avg_rating)/(review_count)
				prod_obj.avg_rating = cal_rating
				prod_obj.save()
			else:
				OrderedProductReviews.objects.create(user=request.user, product=prod_obj, rating=rating, order = ord_obj)

				# change overall rating of product 

				review_count = OrderedProductReviews.objects.filter(product=prod_obj).count()
				print(review_count,prod_obj.avg_rating*review_count)
				cal_rating = ((prod_obj.avg_rating*review_count) + int(rating))/(review_count)
				print(cal_rating)
				prod_obj.avg_rating = cal_rating
				prod_obj.save()

			return Response({
			'message':'Your rating submitted successfully'
			},200)

		return Response({
			'message':'Please provide order_detail_id and rating both'
			},400)


from rest_framework.authentication import SessionAuthentication
class CancelOrderAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [SessionAuthentication]

	def post(self, request):
		data = request.data
		user = request.user

		serializer = CancelOrderSerializer(data=data)
		if serializer.is_valid():

			# cancel order 
			try:
				obj = OrderedProductStatus.objects.get(id = data.get('order_detail_id'))
				
				# check current status of product 

				obj.order_status='5'
				obj.save()

				# save change status for order 

				OrderStatusChangeDate.objects.create(status_change_by=user, order = obj, order_status='5')
			except:
				return Response({
					'message':'Invalid order_detail_id'
					},400)
			# save cancelation reason

			CancelReason.objects.create(cancel_reason="" ,cancel_description=data.get('cancel_description'),order=obj)
			return Response({
					'message':'Order cancelled successfully'
					},200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


from django.utils import timezone

class ReturnOrderAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data

		serializer = ReturnOrderSerializer(data=data)
		if serializer.is_valid():
			bank_holder_name = data.get('bank_holder_name')
			ifsc_code = data.get('ifsc_code')
			branch_addr = data.get('branch_addr')
			bank_name = data.get('bank_name')
			ifsc_code = data.get('ifsc_code')

			# return order 
			try:
				obj = OrderedProductStatus.objects.get(id = data.get('order_detail_id'))
			except:
				return Response({
					'message':'Invalid order_detail_id'
					},400)

			# return if no offer available

			if int(obj.cart.selected_colour.offer) > 0:
				return Response({
				'message':'Discounted product is not eligible for return .Please read our return policies'
				}, 400)

			# 5 days return check

			if (timezone.now()-obj.created).days > 4:
				return Response({
					'message': 'Product is not eligible for return .Please read our return policies'
				}, 400)

			# check bank detail is provided or not in case of COD
			if obj.order.payment == '2':
				bank_holder_name = data.get('bank_holder_name')
				ifsc_code = data.get('ifsc_code')
				branch_addr = data.get('branch_addr')
				bank_name = data.get('bank_name')
				ifsc_code = data.get('ifsc_code')

				if bank_holder_name=='' or ifsc_code=='' or  ifsc_code=='':
					return Response({
								'message': 'Please provide bank account detail for refund'
								}, 400)
			# change status
			obj.order_status = '7'
			obj.save()
			
			# save cancelation reason

			ReturnReason.objects.create(return_reason="", return_description=data.get('return_description'),order=obj)
			
			# save bank detail for refund for cash on delievey method

			RefundMoneyBankDetails.objects.create(user=request.user,order=obj,
				bank_holder_name=bank_holder_name,bank_name=bank_name,
				branch_addr=branch_addr,account_number=data.get('account_number'), ifsc_code=ifsc_code)
			return Response({
					'message': 'Return request submitted successfully'
					},200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)



class ExchangeOrderAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data

		serializer = ExchangeOrderSerializer(data=data)
		if serializer.is_valid():
			try:
				obj = OrderedProductStatus.objects.get(id = data.get('order_detail_id'))
			except:
				return Response({
					'message':'Invalid order_detail_id'
					},400)

			# exchange if no offer available

			if int(obj.cart.selected_colour.offer) > 0:
				return Response({
				'message':'Discounted product is not eligible for exchange .Please read our return policies'
				}, 400)

			# 5 days exchange check

			if (timezone.now()-obj.created).days > 100:
				return Response({
					'message': 'Product is not eligible for exchange .Please read our exchange policies'
				}, 400)

			# check colour is valid or not 
			colour_qs = obj.cart.product.available_colours.filter(id=data.get('selected_colour'), is_active=True, is_out_of_stock=False)
			if not colour_qs.exists():
				return Response({
					'message':'Invalid selected_colour'
					},400)
			
			# check size is correct or not 

			size_qs = colour_qs.first().size_and_qty.filter(size=data.get('selected_size'), stock_status=True)
			if not size_qs.exists():
				return Response({
					'message': 'This size is not available with this colour'
					}, 400)
				
			# price of previous product
			# coupon applied or not
			# single product
			# multiple product

			# deatil of orders like payemnt payment method etc

			main_order_obj = obj.order


			no_of_product_ordered = main_order_obj .cart.all().count()
			if no_of_product_ordered==1:
				# only this product is ordered
				# no need to check coupon
				ammount_paid = main_order_obj.grand_total
			# if more than one product was added than we will check special price only
			else:
				ammount_paid = obj.cart.selected_colour.special_price
			current_price_of_product = colour_qs.first().special_price
			product_obj = obj.cart.product
			# add to cart as exchange product
			cart_obj = CustomerProductCart.objects.create(user=request.user, product = product_obj,
											   selected_size = data.get('selected_size'),
											   selected_colour = colour_qs.first(),
											   is_exchange_product=True, is_ordered=True
											   )

			# save exchange cart deatil
			ExchangeCart.objects.create(user=request.user, order =obj, exchange_description=data.get('exchange_description'))

			# image_qs = ProductImageByColour.objects.filter(product_colour_id=colour_qs)
			# if image_qs.exists():
			# 	image = image_qs.first().image
			# else:
			image = product_obj.main_img
			product_detail = {
				"name":product_obj.name,
				"product_image":image.url,
				"selected_size": data.get('selected_size'),
				"product_description":product_obj.description,
				"avg_rating": product_obj.avg_rating,
				"special_price": obj.cart.selected_colour.special_price,
				"actual_price": obj.cart.selected_colour.actual_price
				
			}

			# check how much amount is required to be paid
			grand_total = current_price_of_product-int(ammount_paid)
			if grand_total >0:
				grand_total = grand_total
				is_payment_required = True
				is_refund_required = False
				message = "Please pay ${} for exchange of product".format(grand_total)
			elif grand_total < 0:
				grand_total = -(grand_total)
				is_payment_required = False
				is_refund_required = True
				message ="${} will be refunded via selected mode of payment in 3-5 business days".format(grand_total)
			else:
				grand_total = 0
				is_payment_required = False
				is_refund_required = False
				message =""
				
			payment_detail = {
				"initial_ammount": ammount_paid,
				"exchange_amount": current_price_of_product,
				"grand_total": grand_total,
				"shipping_charges": 0,
				"message_text": message,
				"previous_payment_mode": main_order_obj.payment,
			}
			order_detail = {
				"is_payment_required" : is_payment_required,
				"is_refund_required" : is_refund_required,
				"cart_id" :cart_obj.id,
				"order_detail_id":obj.id,
				"address":obj.order.address.id
			}
			return Response({
				"product_detail": product_detail,
				"payment_detail": payment_detail,
				"order_detail": order_detail,

			}, 200)
		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)



class ChangeOrderStatusOrderAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [SessionAuthentication]

	def post(self, request, *args ,**kwargs):
		data = request.data
		user = request.user
		order_detail_id = data.get('order_detail_id')
		status_id = data.get('status_id')

		# change status  order
		try:
			obj = OrderedProductStatus.objects.select_related(None).get(id = data.get('order_detail_id'))
			previous_status = obj.order_status
			new_status = status_id
			# check current status of product
			obj.order_status = status_id
			obj.save()
			# save change status for order 

			order_obj = OrderStatusChangeDate.objects.create(status_change_by=user, order = obj, order_status=status_id)
			to = obj.user.email
			plain_message = None
			from_email = 'Viewed <webmaster@localhost>'
			subject = 'Product ' + obj.cart.product.name
			message_text = render_to_string('mails/status_change_mail.html', {
				'user':request.user,
				'product':obj.cart.product.name,
				'previousStatus':previous_status,
				'newStatus':new_status,
				'track_url':'https://giyf.com'
			})
			mail.send_mail(subject, plain_message, from_email, [to], html_message=message_text)
		except:
			return Response({
				'message':'Invalid order_detail_id'
				},400)
		# save status change id required reason

		return Response({
				'message':'Order Status changed successfully'
				},200)


class SaveFileView(APIView):
	def post(self,request,*args,**kwargs):
		myfile = request.FILES.get('file')
		if myfile:
			tres = TempResponse(
				file = myfile,
			)
			tres.save()
			return Response({
				'success':'True',
				'message':'Saved successfully',
				'url':tres.file.url
			},200)
		return Response({
			'success':'False',
			'message':'Please upload file'
		},400)
from rest_framework.generics import (
		CreateAPIView,
		ListAPIView,

	)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
	HTTP_200_OK,
	HTTP_400_BAD_REQUEST,
	HTTP_204_NO_CONTENT,
	HTTP_201_CREATED,
	HTTP_500_INTERNAL_SERVER_ERROR,
	HTTP_404_NOT_FOUND
	)

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
import django_filters
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication

from .serializers import *
from payments.models import *
from orders.models import RefundMoneyBankDetails
import logging
logger = logging.getLogger('accounts')


from orders.api.views import make_order, place_exchange_order

#payment gateway
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

from product.models import CustomerProductCart,Product
import json


from django.core import mail
from django.template.loader import render_to_string

class ChargeAPIView(APIView ,):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request, *args, **kwargs):
		data = request.data
		all_cart_item = dict(request.data).get('cart')
		logger.info(data)
		# print((data))
		### check cart quantity with product available quantity

		if all_cart_item:
			cart_qs = CustomerProductCart.objects.filter(id__in = all_cart_item)
			if cart_qs.exists():
				print(cart_qs)
				for cart_obj in cart_qs:
					product_obj = cart_obj.product

					##  case -1 - if product is inactive or selected colour has been deleted

					if not product_obj.active:
						return Response({
								'status': 'error',
								'message': 'Product '+ product_obj.name  +' is currently not available. Please remove it from cart'

								}, status=400)

					print(cart_obj,'cart_obj')


					# selected colour is not available or may be deleted

					if cart_obj.selected_colour is None or cart_obj.selected_colour.is_active == False:
						return Response({
							'status': 'error',
							'message': 'Your selected colour (' + cart_obj.selected_colour.colour.name +') for ' + product_obj.name + ' is out of stock. Please remove it from cart'

							}, status=400)

					size_qs = cart_obj.selected_colour.size_and_qty.filter(size = cart_obj.selected_size)

					## if selected size has deleted

					if not size_qs.exists():
						return Response({
							'status': 'error',
							'message': 'Your selected size ('+ cart_obj.selected_size +') for ' + product_obj.name + ' is out of stock. Please remove it from cart'

							}, status=400)

					## if selected size is out of stock

					if size_qs.first().available_qty == 0:
						return Response({
							'status': 'error',
							'message': 'Your selected size ('+ cart_obj.selected_size +') for ' + product_obj.name + ' is out of stock. Please remove it from cart'

							}, status=400)
					## if selected size qty is greater than available

					if size_qs.first().available_qty < int(cart_obj.selected_quantity):
						return Response({

							'status': 'error',
							'message': 'Product '+product_obj.name+' has only '+ str(size_qs.first().available_qty) +' quantity left. So Please try with lower quantity.'

							}, status=400)

				### all logic for payment

				if data['payment'] == "1" or data['payment'] == 1: # by card

					serializer = PaymentSerializer(data=data)

					if serializer.is_valid():

						try:
							logger.info(request.user)
							customer = get_or_create_customer(
								request.user,
								data['source_token'],
								data['is_card_save']
							)
							charge = stripe.Charge.create(
								amount = str(data['grand_total'])+'00',
								currency = data['currency'],
								customer = customer, # customer id
								description = 'Payment to buy Product'

							)
							print(charge,'charge',charge.outcome.seller_message)

							if charge:

								payment_history = PaymentHistory.objects.create(user=request.user,payment_type=data['payment'],
									description="Payment to buy product",status_message = charge.outcome.seller_message , payment_id=charge.id,
									amount = charge.amount ,captured=charge.captured,payment_detail=customer)
								print(payment_history,'dfgsdgsdfgsfd')
								# add orders api to save
								order_response = make_order(self,request,*args,**kwargs)

								if order_response['status']==200:
									payment_history.order_id_id = order_response['order_id']
									payment_history.save()
									product_list = order_response['product_list']
									to = request.user.email
									plain_message = None
									from_email = 'Viewed <webmaster@localhost>'
									subject = 'Order placed successfully'
									message_text = render_to_string('mails/product_ordered.html', {
										'user': request.user,
										'product': product_list,
									})
									mail.send_mail(subject, plain_message, from_email, [to], html_message=message_text)
									return Response({
										'status': 'success',
										'message': order_response['message']

										}, status=200)

								return Response({
										'status': 'error',
										'message': order_response['message']

										}, status=400)


						except stripe.error.CardError as e:
						  	# Since it's a decline, stripe.error.CardError will be caught
						  	body = e.json_body
						  	err  = body.get('error', {})

						  	print ("Status is: %s" % e.http_status)
						  	print ("Type is: %s" % err.get('type'))
						  	print ("Code is: %s" % err.get('code'))
						  	print ("Param is: %s" % err.get('param'))
						  	print ("Message is: %s" % err.get('message'))
						except stripe.error.RateLimitError as e:
						  	# Too many requests made to the API too quickly
						  	body = e.json_body
						  	err  = body.get('error', {})
						except stripe.error.InvalidRequestError as e:
						  	# Invalid parameters were supplied to Stripe's API
						  	body = e.json_body
						  	err  = body.get('error', {})
						except stripe.error.AuthenticationError as e:
						  	# Authentication with Stripe's API failed
						  	# (maybe you changed API keys recently)
						  	body = e.json_body
						  	err  = body.get('error', {})
						except stripe.error.APIConnectionError as e:
						  	# Network communication with Stripe failed
						  	body = e.json_body
						  	err  = body.get('error', {})
						except stripe.error.StripeError as e:
						  	# Display a very generic error to the user, and maybe send
						  	# yourself an email
						  	body = e.json_body
						  	err  = body.get('error', {})
						except Exception as e:
						  	# Something else happened, completely unrelated to Stripe

						  	err  = {'message':e}


						### save payment information

						PaymentHistory.objects.create(user=request.user,payment_type=data['payment'],
							description="Payment to buy product",status_message = err.get('message') )

						return Response({
								'status': 'error',
								'message': err.get('message')
								}, status=500)

					return Response(
								serializer.errors,
								 status=400)

				elif data['payment'] =="2" or data['payment'] == 2: # cash on delivery

					order_response = make_order(self, request,*args,**kwargs)

					if order_response['status'] == 200:

						## save in payment_history one by one 
						# order_id = order_response['order_id']

						# orders_qs = OrderedProductStatus.objects.filter(order_id=order_id)
						# for order in orders_qs:
						# 	PaymentHistory.objects.create(user=request.user,payment_type='2',
						# 			description="Payment to by product",status_message = 'Not Paid' , payment_id='',
						# 			amount = charge.amount ,captured=False,payment_detail='',sub_order_id='')


						return Response({
							'status': 'success',
							'message': order_response['message']

							}, status=200)

					return Response({
							'status': 'success',
							'message': order_response['message']

							}, status=200)

				elif data['payment'] =="3" or data['payment'] == 3:
					return Response({
							'status': 'error',
							'message': 'Internet banking is currently not available'

							}, status=400)

				else:
					return Response({
							'status': 'error',
							'message': 'Pls enter currect card type'

							}, status=400)
			return Response({
					'status': 'success',
					'message': 'Wrong cart id'

					}, status=400)

		return Response({
					'status': 'success',
					'message': 'Pls give cart id'

					}, status=400)


# helpers
def get_or_create_customer(user, token, is_card_save):
	logger.info(user, '1111111111111111111')
	customer_qs = StripeCustomer.objects.filter(user = user, source_token = token)
	logger.info(customer_qs)

	if customer_qs.exists():

		return customer_qs.first().stripe_cus_id

	customer = stripe.Customer.create(
		email = user.email,
		source = token,
		name = user.first_name + ' '+user.last_name,
	)

	print(customer,'created')
	logger.info(customer)
	print(is_card_save)
	if is_card_save =='true' or is_card_save == True:
		card = 'XXXX-XXXX-XXXX-'+ customer.sources.data[0].last4
		name = customer.sources.data[0].name
		StripeCustomer.objects.create(user=user,name = name, source_token= token,stripe_cus_id = customer.id, card = card)
	return customer.id


class ListOfSavedCard(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request, *args, **kwargs):
		user = request.user
		qs = StripeCustomer.objects.filter(user=request.user)
		data = ListOfSavedCardSerializer(qs ,many=True).data

		return Response({
			'message':'success',
			'data':data
			}, 200)


class DeleteCardAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def delete(self, request, *args, **kwargs):
		card_id = self.kwargs.get('id')
		try:
			StripeCustomer.objects.get(id=card_id,user=request.user).delete()
			qs = StripeCustomer.objects.filter(user=request.user)
			data = ListOfSavedCardSerializer(qs, many=True).data
			return Response({
				'message': 'successfully deleted',
				'data':data
			}, 200)
		except:
			return Response({
				'message':'Invalid card id'
			}, 400)


class SaveNewCardAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self,request):

		token = request.data.get('source_token')

		if not token == '' or token==None:
			user = request.user
			try:
				customer = stripe.Customer.create(
					email = user.email,
					source = token,
					name = user.first_name + ' '+user.last_name,
				)

				card = 'XXXX-XXXX-XXXX-'+ customer.sources.data[0].last4
				name = customer.sources.data[0].name
				StripeCustomer.objects.create(user=user,name = name, source_token= token,stripe_cus_id = customer.id, card = card)

				return Response({
					'message':'Card added successfully'

					},200)

			except stripe.error.CardError as e:
			  	# Since it's a decline, stripe.error.CardError will be caught
			  	body = e.json_body
			  	err  = body.get('error', {})

			  	print ("Status is: %s" % e.http_status)
			  	print ("Type is: %s" % err.get('type'))
			  	print ("Code is: %s" % err.get('code'))
			  	print ("Param is: %s" % err.get('param'))
			  	print ("Message is: %s" % err.get('message'))
			except stripe.error.RateLimitError as e:
			  	# Too many requests made to the API too quickly
			  	body = e.json_body
			  	err  = body.get('error', {})
			except stripe.error.InvalidRequestError as e:
			  	# Invalid parameters were supplied to Stripe's API
			  	body = e.json_body
			  	err  = body.get('error', {})
			except stripe.error.AuthenticationError as e:
			  	# Authentication with Stripe's API failed
			  	# (maybe you changed API keys recently)
			  	body = e.json_body
			  	err  = body.get('error', {})
			except stripe.error.APIConnectionError as e:
			  	# Network communication with Stripe failed
			  	body = e.json_body
			  	err  = body.get('error', {})
			except stripe.error.StripeError as e:
			  	# Display a very generic error to the user, and maybe send
			  	# yourself an email
			  	body = e.json_body
			  	err  = body.get('error', {})
			except Exception as e:
			  	# Something else happened, completely unrelated to Stripe

			  	err  = {'message':e}

			return Response({
				'message':err.get('message')
				})

		return Response({
				'message':'Please provide source token'

				},400)


class ExchangePayment(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data
		# check all data is proper or not
		serializer = ExchangePaymentSerializer(data=data)
		if not serializer.is_valid():
			error_keys = list(serializer.errors.keys())
			if error_keys:
				error_msg = serializer.errors[error_keys[0]]
				return Response({'message': error_msg[0]}, status=400)
			return Response(serializer.errors, status=400)


		cart_id = data.get('cart_id')
		is_payment_required = serializer.validated_data.get('is_payment_required')
		is_refund_required = serializer.validated_data.get('is_refund_required')

		try:
			cart_qs = CustomerProductCart.objects.filter(id = cart_id, is_exchange_product=True)
		except:
			return Response({
				"message": "wrong cart id"
				})

		if is_payment_required==True: # case-1
			# all logic for payment
			if data['payment'] == "1" or data['payment'] == 1:  # by card

				serializer = ExchangePaymentSerializerForCardPayment(data=data)

				if serializer.is_valid():

					try:
						customer = get_or_create_customer(
							request.user,
							data['source_token'],
							data['is_card_save']
						)
						charge = stripe.Charge.create(
							amount=str(data['grand_total']) + '00',
							currency=data['currency'],
							customer=customer,  # customer id
							description='Payment to exchange Product'

						)
						print(charge, 'charge', charge.outcome.seller_message)

						if charge:

							payment_history = PaymentHistory.objects.create(user=request.user,
																			payment_type=data['payment'],
																			description="Payment for exchange",
																			status_message=charge.outcome.seller_message,
																			payment_id=charge.id,
																			amount=charge.amount,
																			captured=charge.captured,
																			payment_detail=customer,
																			is_payment_for_exchange=True)
							# add orders api to save
							order_response = place_exchange_order(self, request)

							if order_response['status'] == 200:
								payment_history.order_id_id = order_response['order_id']
								payment_history.save()
								return Response({
									'status': 'success',
									'message': order_response['message']

								}, status=200)

							return Response({
								'status': 'error',
								'message': order_response['message']

							}, status=400)


					except stripe.error.CardError as e:
						# Since it's a decline, stripe.error.CardError will be caught
						body = e.json_body
						err = body.get('error', {})

						print("Status is: %s" % e.http_status)
						print("Type is: %s" % err.get('type'))
						print("Code is: %s" % err.get('code'))
						print("Param is: %s" % err.get('param'))
						print("Message is: %s" % err.get('message'))
					except stripe.error.RateLimitError as e:
						# Too many requests made to the API too quickly
						body = e.json_body
						err = body.get('error', {})
					except stripe.error.InvalidRequestError as e:
						# Invalid parameters were supplied to Stripe's API
						body = e.json_body
						err = body.get('error', {})
					except stripe.error.AuthenticationError as e:
						# Authentication with Stripe's API failed
						# (maybe you changed API keys recently)
						body = e.json_body
						err = body.get('error', {})
					except stripe.error.APIConnectionError as e:
						# Network communication with Stripe failed
						body = e.json_body
						err = body.get('error', {})
					except stripe.error.StripeError as e:
						# Display a very generic error to the user, and maybe send
						# yourself an email
						body = e.json_body
						err = body.get('error', {})
					except Exception as e:
						# Something else happened, completely unrelated to Stripe

						err = {'message': e}

					### save payment information

					PaymentHistory.objects.create(user=request.user, payment_type=data['payment'],
												  description="Payment to exchange product",
												  status_message=err.get('message'))

					return Response({
						'status': 'error',
						'message': err.get('message')
					}, status=400)

				error_keys = list(serializer.errors.keys())
				if error_keys:
					error_msg = serializer.errors[error_keys[0]]
					return Response({'message': error_msg[0]}, status=400)
				return Response(serializer.errors, status=400)

			# user may select cod option for exchange

			elif data['payment'] == "2" or data['payment'] == 2:  # cash on delivery
				serializer = ExchangePaymentSerializerForCODPayment(data=data)
				if not serializer.is_valid():
					error_keys = list(serializer.errors.keys())
					if error_keys:
						error_msg = serializer.errors[error_keys[0]]
						return Response({'message': error_msg[0]}, status=400)
					return Response(serializer.errors, status=400)


				order_response = place_exchange_order(self, request)

				if order_response['status'] == 200:
					return Response({
						'status': 'success',
						'message': order_response['message']

					}, status=200)

				return Response({
					'status': 'success',
					'message': order_response['message']

				}, status=400)

			else:
				return Response({
					'status': 'error',
					'message': 'Pls enter currect payment type'

				}, status=400)

		if is_refund_required==True:
			if data.get('mode_of_refund')==1 or data.get('mode_of_refund')=="1": #by card
				serializer =RefundForCardSerializer(data=data)
				if not serializer.is_valid():
					error_keys = list(serializer.errors.keys())
					if error_keys:
						error_msg = serializer.errors[error_keys[0]]
						return Response({'message': error_msg[0]}, status=400)
					return Response(serializer.errors, status=400)

				# palce order
				order_response = place_exchange_order(self, request)

			elif data.get('mode_of_refund')==2 or data.get('mode_of_refund')=="2": # if COD
				serializer = RefundForCODSerializer(data=data)
				if not serializer.is_valid():
					error_keys = list(serializer.errors.keys())
					if error_keys:
						error_msg = serializer.errors[error_keys[0]]
						return Response({'message': error_msg[0]}, status=400)
					return Response(serializer.errors, status=400)

				# palce order
				order_response = place_exchange_order(self, request)

				# save refund bank detail
				RefundMoneyBankDetails.objects.create(user=request.user, order_id=order_response['order_id'],
													  bank_holder_name=data.get('bank_holder_name'),
													  bank_name=data.get('bank_name'),
													  account_number=data.get('account_number'),
													  ifsc_code=data.get('ifsc_code'),
													  branch_addr=data.get('branch_addr'),
													  is_exchange=True)  # exchange_previous_order=""
			else:
				return Response({
					'message':'Please provide currect mode of refund'
				})

			if order_response['status'] == 200:
				return Response({
					'status': 'success',
					'message': order_response['message']

				}, status=200)

			return Response({
				'status': 'success',
				'message': order_response['message']

			}, status=400)


		if is_refund_required==False and is_payment_required==False:
			serializer = NoRefundNoPaymentSerializer(data=data)
			if not serializer.is_valid():
				error_keys = list(serializer.errors.keys())
				if error_keys:
					error_msg = serializer.errors[error_keys[0]]
					return Response({'message': error_msg[0]}, status=400)
				return Response(serializer.errors, status=400)

			order_response = place_exchange_order(self, request)


			if order_response['status'] == 200:
				return Response({
					'status': 'success',
					'message': order_response['message']

				}, status=200)

			return Response({
				'status': 'failed',
				'message': order_response['message']

			}, status=400)

		else:
			return Response({
				'message':'not valid type boolean'
				},400)

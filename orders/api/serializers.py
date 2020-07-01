

from rest_framework.serializers import(
     ModelSerializer,
     CharField,
     SerializerMethodField,
     Serializer,

     )

from orders.models import *
from rest_framework.exceptions import APIException
class APIException400(APIException):
    status_code = 400


class DeliveryAddressViewSerializer(ModelSerializer):
	class Meta:
		model = CustomerAddress
		fields  = '__all__'


class DeliveryAddressAddSerializer(ModelSerializer):
	name = CharField(max_length=1000, error_messages={'max_length': 'Please enter valid name'})
	state = CharField(allow_blank=True)
	class Meta:
		model = CustomerAddress
		fields  = [
			'name',
			'country_code',
			'phonenum',
			'city',
			'pincode',
			'state',
			'area_street',
			'flat_building',
			'addr_type',
			'landmark',
			'lat',
			'log',
		]

	def validate(self,data):
		print(len(data['phonenum']))
		if not data['phonenum'].isdigit() or  not len(data['phonenum']) < 13:
			raise APIException400({
                'message':'Please correct your number',
                
                })
		if not data['pincode'].isdigit() or not len(data['pincode']) < 8:
			raise APIException400({
                'message':'Please correct your pin code',
                })
		return data


class MakeOrderAPIViewSerializer(ModelSerializer):
	coupon_code  =  CharField(allow_blank=True)

	class Meta:
		model = CustomerOrders
		fields  = [
			'cart',
			'address',
			'payment',
			'is_coupon_applied',
			'item',
			'coupon_code',
			'coupon_off',
			'price',
			'saved_amount',
			'shipping_charges',
			'grand_total'
			]


class ProductOrderedDetailSerializer(ModelSerializer):
	address = SerializerMethodField()
	is_coupon_applied = SerializerMethodField()
	
	def is_coupon_applied(self, instance):
		if instance.coupon_code=='' or instance.coupon_code==None:
			return False
		return True

	def get_address(self,instance):
		data = DeliveryAddressAddSerializer(instance.address).data
		return data

	class Meta:
		model = CustomerOrders
		fields  = [
			'address',
			'payment',
			'is_coupon_applied',
			]


class OrderStatusChangeDateSerializer(ModelSerializer):
	created = SerializerMethodField()

	def get_created(self,instance):
		return (instance.created).strftime("%a, %b%d '%y")

	class Meta:
		model = OrderStatusChangeDate
		fields = [
			'created',
			'order_status'
		]


from product.api.serializers import CustomerCartAllProductListSerializer
from dateutil.parser import parse


class AllOrderProductHistorySerializer(ModelSerializer):
	product_detail = SerializerMethodField()
	order_id =SerializerMethodField()
	order_date = SerializerMethodField()
	latest_status = SerializerMethodField()

	def get_latest_status(self, instance):
		obj = OrderStatusChangeDate.objects.filter(order=instance).order_by('-created').first()
		data = OrderStatusChangeDateSerializer(obj).data
		return data

	def get_order_date(self, instance):
		return (instance.created).strftime("%a, %b%d '%y")

	def get_product_detail(self, instance):
		data = CustomerCartAllProductListSerializer(instance.cart).data
		return data

	def get_order_id(self,instance):
		return instance.order.id


	class Meta:
		model = OrderedProductStatus
		fields = [
			'id',
			'created',
			'order_status',
			'order_id',
			'product_detail',
			'order_date',
			'latest_status'

		]

class OrderedProductReviewsSerializer(ModelSerializer):
	class Meta:
		model = OrderedProductReviews
		fields = '__all__'



class OrderdProductHistorySerializer(ModelSerializer):
	product_detail = SerializerMethodField()
	order_detail = SerializerMethodField()
	# reviews  =SerializerMethodField()
	order_status = SerializerMethodField()
	user_rating = SerializerMethodField()
	order_id =SerializerMethodField()


	def get_product_detail(self,instance):
		data = CustomerCartAllProductListSerializer(instance.cart).data
		return data

	def get_order_status(self, instance):
		return int(instance.order_status)

	def get_order_detail(self,instance):
		data = ProductOrderedDetailSerializer(instance.order).data
		return data

	def get_user_rating(self,instance):
		review_obj = OrderedProductReviews.objects.filter(user = self.context['request'].user,order=instance)
		if review_obj.exists():
			return review_obj.first().rating
		return 0

	def get_order_id(self,instance):
		return instance.order.id

	# def get_reviews(self,instance):
	# 	qs = OrderedProductReviews.objects.filter(user = self.context['request'].user, order=instance.id)
	# 	if qs.exists():

	# 		data = OrderedProductReviewsSerializer(qs.first()).data
	# 		return data
	# 	return []
	class Meta:
		model = OrderedProductStatus
		fields = [
			'id',
			'created',
			'order_status',
			'order_detail',
			'product_detail',
			'track_id',
			'track_url',
			'user_rating',
			'order_id'
			# 'reviews',

		]

class CancelOrderSerializer(Serializer):
	order_detail_id = CharField(error_messages = {'required': 'order_detail_id key is required', 'blank': 'order_detail_id is required'})
	# cancel_reason = CharField(error_messages = {'required': 'cancel_reason key is required', 'blank': 'cancel_reason is required'})
	cancel_description = CharField(error_messages = {'required': 'cancel_description key is required','blank': 'cancel description required'})


class ReturnOrderSerializer(Serializer):
	order_detail_id = CharField(error_messages = {'required': 'order_detail_id key is required', 'blank': 'order_detail_id is required'})
	# return_reason = CharField(error_messages = {'required': 'cancel_reason key is required', 'blank': 'cancel_reason is required'})
	return_description = CharField(error_messages = {'required': 'return_description key is required','blank': 'return descriptionis required'})
	bank_holder_name = CharField(allow_blank=True, error_messages = {'required': 'bank_holder_name key is required'})
	bank_name = CharField(allow_blank=True, error_messages = {'required': 'bank_name key is required'})
	account_number = CharField(allow_blank=True, error_messages = {'required': 'account_number key is required'})
	ifsc_code = CharField(allow_blank=True, error_messages = {'required': 'ifsc_code key is required'})
	branch_addr = CharField(allow_blank=True, error_messages = {'required': 'branch_addr key is required'})


class ExchangeOrderSerializer(Serializer):
	order_detail_id = CharField(error_messages = {'required': 'order_detail_id key is required', 'blank': 'order_detail_id is required'})
	exchange_description = CharField(error_messages = {'required': 'exchange_description key is required', 'blank': 'exchange description is required'})
	selected_colour = CharField(error_messages = {'required': 'selected_colour key is required', 'blank': 'selected colour is required'})
	selected_size = CharField(error_messages = {'required': 'selected_size key is required', 'blank': 'selected size is required'})



from rest_framework.serializers import(
	 ModelSerializer,
	 SerializerMethodField,
	 Serializer,
	 CharField,
	 BooleanField

	 )

from payments.models import *
from rest_framework.exceptions import APIException


class APIException400(APIException):
	status_code = 400


class PaymentSerializer(Serializer):
	source_token 	= CharField(required=True)
	grand_total 	= CharField(required=True)
	currency 		= CharField(required=True)


class ListOfSavedCardSerializer(ModelSerializer):
	class Meta:
		model 	= StripeCustomer 
		fields 	= ['card','source_token','name','id']


class ExchangePaymentSerializer(Serializer):
	cart_id = CharField(error_messages = {'required': 'cart_id key is required', 'blank': 'cart_id is required'})
	address = CharField(allow_blank=True,error_messages = {'required': 'address key is required'})
	payment = CharField(allow_blank=True,error_messages = {'required': 'payment key is required'})
	grand_total = CharField(allow_blank=True,error_messages = {'required': 'grand_total key is required'})
	currency = CharField(allow_blank=True,error_messages = {'required': 'currency key is required'})
	source_token = CharField(allow_blank=True,error_messages = {'required': 'source_token key is required'})
	is_card_save = BooleanField(required=False,error_messages = {'required': 'is_card_save key is required'})
	bank_holder_name = CharField(allow_blank=True, error_messages = {'required': 'bank_holder_name key is required'})
	bank_name = CharField(allow_blank=True, error_messages = {'required': 'bank_name key is required'})
	account_number = CharField(allow_blank=True, error_messages = {'required': 'account_number key is required'})
	ifsc_code = CharField(allow_blank=True, error_messages = {'required': 'ifsc_code key is required'})
	branch_addr = CharField(allow_blank=True, error_messages = {'required': 'branch_addr key is required'})
	is_payment_required = BooleanField(error_messages = {'required': 'is_payment_required key is required', 'blank': 'is_payment_required is required'})
	is_refund_required = BooleanField(error_messages = {'required': 'is_refund_required key is required', 'blank': 'is_refund_required is required'})
	order_detail_id = CharField(error_messages = {'required': 'order_detail_id key is required', 'blank': 'order_detail_id is required'})



class ExchangePaymentSerializerForCardPayment(Serializer):
	source_token = CharField(error_messages = {'required': 'source_token key is required','blank': 'source_token is required'})
	grand_total = CharField(error_messages = {'required': 'grand_total key is required', 'blank': 'grand_total is required'})
	currency = CharField(error_messages = {'required': 'currency key is required','blank': 'currency is required'})
	payment= CharField(error_messages = {'required': 'paymentkey is required','blank': 'payment is required'})
	is_card_save = BooleanField(required=True, error_messages = {'required': 'is_card_save key is required','blank': 'is_card_save is required'})
	address = CharField(error_messages = {'required': 'address key is required','blank': 'address is required'})
	special_price = CharField(error_messages = {'required': 'special_price key is required','blank': 'special_price is required'})
	actual_price = CharField(error_messages = {'required': 'actual_price key is required','blank': 'actual_price is required'})



class ExchangePaymentSerializerForCODPayment(Serializer):
	grand_total = CharField(error_messages = {'required': 'grand_total key is required', 'blank': 'grand_total is required'})
	currency = CharField(error_messages = {'required': 'currency key is required','blank': 'currency is required'})
	payment = CharField(allow_blank=True,error_messages = {'required': 'payment key is required','blank': 'payment is required'})
	address = CharField(error_messages = {'required': 'address key is required','blank': 'address is required'})
	special_price = CharField(error_messages = {'required': 'special_price key is required','blank': 'special_price is required'})
	actual_price = CharField(error_messages = {'required': 'actual_price key is required','blank': 'actual_price is required'})



class RefundForCardSerializer(Serializer):
	currency = CharField(error_messages = {'required': 'currency key is required','blank': 'currency is required'})
	address = CharField(error_messages = {'required': 'address key is required','blank': 'address is required'})
	special_price = CharField(error_messages = {'required': 'special_price key is required','blank': 'special_price is required'})
	actual_price = CharField(error_messages = {'required': 'actual_price key is required','blank': 'actual_price is required'})
	mode_of_refund = CharField(error_messages = {'required': 'mode_of_refund key is required','blank': 'mode_of_refund is required'})


# if mode of refund is cod
class RefundForCODSerializer(Serializer):
	currency = CharField(error_messages = {'required': 'currency key is required','blank': 'currency is required'})
	address = CharField(error_messages = {'required': 'address key is required','blank': 'address is required'})
	special_price = CharField(error_messages = {'required': 'special_price key is required','blank': 'special_price is required'})
	actual_price = CharField(error_messages = {'required': 'actual_price key is required','blank': 'actual_price is required'})
	bank_holder_name = CharField(error_messages = {'required': 'bank_holder_name key is required','blank': 'bank_holder_name is required'})
	bank_name = CharField( allow_blank=True, error_messages = {'required': 'is_payment_required key is required',})
	account_number = CharField(error_messages = {'required': 'account_number key is required','blank': 'account_number is required'})
	ifsc_code = CharField( error_messages = {'required': 'ifsc_code key is required','blank': 'ifsc_code is required'})
	branch_addr = CharField( allow_blank=True, error_messages = {'required': 'branch_addr key is required'})
	mode_of_refund = CharField(error_messages = {'required': 'mode_of_refund key is required','blank': 'mode_of_refund is required'})


class NoRefundNoPaymentSerializer(Serializer):
	currency = CharField(error_messages = {'required': 'currency key is required','blank': 'currency is required'})
	address = CharField(error_messages = {'required': 'address key is required','blank': 'address is required'})
	special_price = CharField(error_messages = {'required': 'special_price key is required','blank': 'special_price is required'})
	actual_price = CharField(error_messages = {'required': 'actual_price key is required','blank': 'actual_price is required'})



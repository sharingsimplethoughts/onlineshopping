from django.db import models
from django.contrib.auth.models import User

PAYMENT_METHOD = (('1', 'Card'),('3', 'Net banking'),('2' ,'Cash on delivery'))
PAYMENT_STATUS = (('1','Successed'),('2','Failed'))
from django.utils import timezone
from orders.models import CustomerOrders,OrderedProductStatus

class StripeCustomer(models.Model):
	user 		   = models.ForeignKey(User, null=True ,on_delete=models.SET_NULL)
	stripe_cus_id  = models.CharField(max_length=300,blank=True,null=True)
	source_token   = models.CharField(max_length =300,blank=True,null=True)
	card           = models.CharField(max_length=40,blank=True,null=True)
	name           = models.CharField(max_length = 40,blank=True,null=True)
	created        = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.id)


class PaymentHistory(models.Model):
	user 		   		= models.ForeignKey(User, null=True ,on_delete=models.SET_NULL)
	description    		= models.CharField(max_length=200)
	payment_type   		= models.CharField(max_length=30,choices=PAYMENT_METHOD)
	status_message 		= models.TextField(blank=True,null=True)
	payment_id     		= models.CharField(max_length=200,blank=True,null=True)
	amount      		= models.CharField(max_length=100,blank=True,null=True)
	captured            = models.BooleanField(default=False)
	order_id            = models.ForeignKey(CustomerOrders,null=True,on_delete=models.SET_NULL)
	payment_detail      = models.CharField(max_length =100, blank=True,null=True) # card token
	created        		= models.DateTimeField(default=timezone.now)

	## used in case of more than one product is orderd with same order id or in case of COD status
	sub_order_id        = models.ForeignKey(OrderedProductStatus, blank=True,null=True, on_delete=models.CASCADE)

	cod_accepted_user 	= models.ForeignKey(User, blank=True, null=True, related_name ="cod_accepted_user", on_delete=models.SET_NULL)
	
	cod_accepted_date   = models.DateTimeField(blank=True,null=True)

	is_payment_for_exchange = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id)


class MemberPaymentHistory(models.Model):
	send_by 		   	= models.ForeignKey(User, null=True, related_name="send_by", on_delete=models.SET_NULL)
	description    		= models.CharField(max_length=200)
	sub_order_id        = models.ForeignKey(OrderedProductStatus, blank=True,null=True, on_delete=models.CASCADE)
	order_id            = models.ForeignKey(CustomerOrders,null=True, on_delete=models.SET_NULL)
	amount              = models.CharField(max_length=30, blank=True, null=True)
	send_to             = models.ForeignKey(User, related_name="send_to", null=True ,on_delete=models.SET_NULL)
	created        		= models.DateTimeField(default=timezone.now)
	payment_id     		= models.CharField(max_length=200,blank=True,null=True)

	def __str__(self):
		return str(self.id)
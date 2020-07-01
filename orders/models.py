from django.db import models
from django.contrib.auth.models import User
from product.models import Product,CustomerProductCart,CouponCode, Product,ProductAvailableColourWithSizeQty
from django.core.validators import MaxValueValidator, MinValueValidator

ADDTYPE = (('1', 'Work'), ('2', 'Home'), ('3' ,'Other'))
PAYMENT_METHOD = (('1', 'Card'), ('3', 'Net banking'), ('2','Cash on delivery'))

ORDER_STATUS  = (('1', '0rdered'), ('2', 'Packed'), ('3', 'Shipped'),
	('4', 'Delivered'), ('5', 'Cancelled'), ('6', 'Out for delivery'),
	('7', 'returned'), ('8', 'return accepted'), ('9', 'return completed and refuned'),
	('10', 'exchange'), ('11' ,'pickuped and exchanged'), ('12' ,'delivered and exchanged'))


class CustomerAddress(models.Model):
	user 	 		= models.ForeignKey(User, on_delete=models.CASCADE)
	name   			= models.CharField(max_length=1000)
	country_code    = models.CharField(max_length=10)
	phonenum 		= models.CharField(max_length=15)
	city     		= models.CharField(max_length=40)
	pincode      	= models.CharField(max_length=10)
	state    		= models.CharField(max_length=30, blank=True)
	area_street 	= models.CharField(max_length=100,blank=True,null=True)
	flat_building 	= models.CharField(max_length=100,blank=True,null=True)
	addr_type       = models.CharField(max_length=10,choices=ADDTYPE)
	landmark 		= models.CharField(max_length=100,blank=True,null=True)
	
	# in case of pin point address

	lat             = models.CharField(max_length=30,blank=True,null=True)
	log             = models.CharField(max_length=30,blank=True,null=True)


	# not delete address when already attached with any order
	
	is_active      = models.BooleanField(default=True)


	def __str__(self):
		return self.user.first_name + '-'+ str(self.id)


class CustomerOrders(models.Model):
	'''
	ongoing and history all other stuffs
	'''
	user  				= models.ForeignKey(User, on_delete=models.CASCADE)
	cart 				= models.ManyToManyField(CustomerProductCart,blank=True)
	address     		= models.ForeignKey(CustomerAddress, null=True , on_delete=models.SET_NULL)
	payment     		= models.CharField(max_length=50, blank=True, choices=PAYMENT_METHOD)

	# price detail 

	is_coupon_applied   = models.BooleanField(default=False)
	coupon_code         = models.CharField(blank=True,null=True ,max_length=30 )

	item                = models.CharField(max_length=5,blank=True, null=True)
	price               = models.CharField(max_length=10,blank=True, null=True)
	saved_amount        = models.CharField(max_length=10,blank=True, null=True)
	shipping_charges    = models.CharField(max_length=10,blank=True, null=True)
	coupon_off      	= models.CharField(max_length=10, blank=True, null=True)
	grand_total         = models.CharField(max_length=10,blank=True, null=True)
	created     		= models.DateTimeField(auto_now_add=True)
	is_exchange         = models.BooleanField(default=False)
	is_refund_required  = models.BooleanField(default=False)
	exchange_previous_order = models.ForeignKey('orders.OrderedProductStatus', blank=True ,null=True, related_name="exchange_previous", on_delete=models.CASCADE)

	def __str__(self):
		return self.user.first_name + '-' + str(self.id)

	
class OrderedProductStatus(models.Model):
	user  				= models.ForeignKey(User, on_delete=models.CASCADE)
	order   			= models.ForeignKey(CustomerOrders, null=True , on_delete=models.SET_NULL )
	cart 				= models.ForeignKey(CustomerProductCart, null=True , on_delete=models.SET_NULL )
	order_status        = models.CharField(max_length = 2,default= 1, choices=ORDER_STATUS)
	created     		= models.DateTimeField(auto_now_add=True)
	track_id            = models.CharField(max_length=500,blank=True)
	track_url 			= models.CharField(max_length=500, blank=True)

	def __str__(self):
		return self.user.first_name + '-'+ str(self.id) +'-'+ str(self.order)




class OrderedProductReviews(models.Model):
	'''
	feedback of user after delivery of product
	after rating avg_rating should be change
	'''
	order             	= models.ForeignKey(OrderedProductStatus, on_delete=models.CASCADE)
	product             = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
	user                = models.ForeignKey(User, on_delete=models.CASCADE)
	rating              = models.PositiveIntegerField( validators=[MaxValueValidator(5), MinValueValidator(1)])
	content             = models.TextField(blank=True,null=True)
	created             = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.order) +' - '+str(self.user)+' - '+str(self.rating)


class OrderStatusChangeDate(models.Model):
	status_change_by   = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

	order             	= models.ForeignKey(OrderedProductStatus, on_delete=models.CASCADE)
	created             = models.DateTimeField(auto_now_add=True)
	order_status        = models.CharField(max_length = 2,default= 1, choices=ORDER_STATUS)


	def __str__(self):
		return str(self.order)+' - '+str(self.order_status)


class CancelReason(models.Model):
	"""
	to save cancellation reasons
	"""

	order             	= models.ForeignKey(OrderedProductStatus, on_delete=models.CASCADE)
	cancel_reason      	= models.CharField(max_length=150, blank=True)
	cancel_description  = models.TextField(blank=True)
	created             = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return str(self.order)


class ReturnReason(models.Model):
	"""
	to save return reasons
	"""
	order             	= models.ForeignKey(OrderedProductStatus, on_delete=models.CASCADE)
	return_reason      	= models.CharField(max_length=150, blank=True)
	return_description  = models.TextField(blank=True)
	created             = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return str(self.order)


class RefundMoneyBankDetails(models.Model):
	"""
	to save detail of bank account for refund money
	"""
	user                = models.ForeignKey(User, on_delete=models.CASCADE)
	order             	= models.ForeignKey(OrderedProductStatus, on_delete=models.CASCADE)
	bank_holder_name    = models.CharField(max_length=100)
	bank_name           = models.CharField(max_length=100,blank=True)
	account_number      = models.CharField(max_length=50)
	ifsc_code           = models.CharField(max_length=25)
	branch_addr         = models.CharField(max_length=50,blank=True)
	created             = models.DateTimeField(auto_now_add=True)
	is_exchange         = models.BooleanField(default=False)
	is_return           = models.BooleanField(default=False)
	exchange_previous_order = models.ForeignKey(OrderedProductStatus, blank=True ,null=True, related_name="exchange_previous_order", on_delete=models.CASCADE)

	def __str__(self):
		return str(self.order) +' - '+ str(self.user)


class ExchangeCart(models.Model):

	user                	= models.ForeignKey(User, on_delete=models.CASCADE)
	order      				= models.ForeignKey(OrderedProductStatus, on_delete=models.CASCADE)
	exchange_description  	= models.TextField(blank=True)


	def __str__(self):
		return str(self.order) +' - '+ str(self.user)


class TempResponse(models.Model):
	res = models.TextField(default='')
	file = models.FileField(upload_to="user/profileimg",default='')

	def __str__(self):
		return str(self.id)

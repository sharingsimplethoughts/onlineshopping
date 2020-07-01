from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([CustomerAddress, OrderStatusChangeDate,CustomerOrders,ReturnReason,ExchangeCart,RefundMoneyBankDetails,CancelReason,OrderedProductStatus,OrderedProductReviews])
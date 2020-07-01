from django.urls import path

from .views import *

urlpatterns = [

	path('make_payment_and_place_order', ChargeAPIView.as_view(), name='charge'),
	path('get_all_cards', ListOfSavedCard.as_view(), name='get_cards'),
	path('add_card', SaveNewCardAPIView.as_view(), name='add_card'),
	path('make_payment_and_exchange_product', ExchangePayment.as_view(), name='make_payment_and_exchange_product'),
	path('delete_card/<str:id>', DeleteCardAPIView.as_view(), name='delete_card'),

]

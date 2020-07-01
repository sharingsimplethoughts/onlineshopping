from django.urls import path

from .views import *

urlpatterns = [

    path('defaultsize_product_3d_view' ,DefaultSizeAPIView.as_view(), name="default size"),
    path('save_measurements', SaveMeasurementAPIView.as_view(), name="save sizes"),

]
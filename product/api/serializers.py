from rest_framework.serializers import(
	ModelSerializer,
	SerializerMethodField,
	CharField,
	BooleanField,
	Serializer
	 
	 )
from product.models import * 

from designer_stylist.models import Profile

from django.db.models import Sum

class UserDetailSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = [
			'first_name',
			'last_name',

		]
class HomeImageSerializer(ModelSerializer):
	class Meta:
		model = HomePageImage
		fields = '__all__'

class CategoryListSeializer(ModelSerializer):
	class Meta:
		model = Category
		fields = ['id', 'cat_name', 'cat_image']

class SubCategoryListSeializer(ModelSerializer):
	class Meta:
		model = SubCategory
		fields = '__all__'

class SubSubCategoryListSeializer(ModelSerializer):
	class Meta:
		model = SubSubCategory
		fields = '__all__'


class CategoryListFilterSeializer(ModelSerializer):
	class Meta:
		model = Category
		fields = ['id','cat_name']

class SubCategoryListFilterSeializer(ModelSerializer):
	class Meta:
		model = SubCategory
		fields = ['id','subcat_name' ,'category']

class SubSubCategoryListFilterSeializer(ModelSerializer):
	class Meta:
		model = SubSubCategory
		fields = ['id','subsubcat_name', 'category' ,'subcategory' ]

class ProductAvailableColourSerializer(ModelSerializer):
	class Meta:
		model = ProductAvailableColour
		fields = ['id','colour' ]


class ProductCategoryListSeializer(ModelSerializer):
	class Meta:
		model = Category
		fields = [
			'id',
			'cat_name',

		]

class ProductSubCategoryListSeializer(ModelSerializer):
	class Meta:
		model = SubCategory
		fields = [
			'id',
			'subcat_name',

		]

class ProductSubSubCategoryListSeializer(ModelSerializer):
	class Meta:
		model = SubSubCategory
		fields = [
			'id',
			'subsubcat_name',

		]

class ProductImageSerializer(ModelSerializer):
	class Meta:
		model = ProductImage
		fields = '__all__'


############################## new changes################

class ProductImageByColourSerializer(ModelSerializer):
	class Meta:
		model = ProductImageByColour
		fields = ['image']


class ProductSizeWithQtySerializer(ModelSerializer):
	class Meta:
		model 	=  ProductSizeWithQty
		fields 	= ['id','size','initial_qty','available_qty','stock_status']

class ColourSizeImageSerializer(ModelSerializer):
	product_images = SerializerMethodField()

	def get_product_images(self,instance):
		qs = ProductImageByColour.objects.filter(product_colour_id = instance.id)

		data = ProductImageByColourSerializer(qs, many=True).data
		return data

	class Meta:
		model = ProductAvailableColourWithSizeQty
		fields = ['colour','actual_price','special_price','offer','is_active','product_images']


class ProductListSerializer(ModelSerializer):
	category = ProductCategoryListSeializer()
	subcategory = ProductSubCategoryListSeializer()
	subsubcategory = ProductSubSubCategoryListSeializer()
	colour_and_images = SerializerMethodField()
	is_in_wishlist = SerializerMethodField()
	avg_rating = SerializerMethodField()

	def get_colour_and_images(self,instance):
		obj = instance.available_colours.filter(is_active=True).order_by('special_price')
		if obj.exists():
			data = ColourSizeImageSerializer(obj[0]).data
			return data
		return {}

	def get_avg_rating(self, instance):
		return round(instance.avg_rating, 1)

	def get_is_in_wishlist(self, instance):
		request = self.context.get('request')
		if request:
			user = request.user
			if user.is_authenticated:
				qs = CustomerProductWishList.objects.filter(user =user, product=instance )
				if qs.exists():
					return True
			return False
		return False

	class Meta:
		model = Product
		fields = [
		'id',
		'category',
		'subcategory',
		'subsubcategory',
		'name',
		'avg_rating',
		'qty_sold',
		'main_img',
		'colour_and_images',
		'is_in_wishlist'

		]



class StylistDesignerProductListSerializer(ModelSerializer):
	profile_name = SerializerMethodField()
	category 	= ProductCategoryListSeializer()
	subcategory = ProductSubCategoryListSeializer()
	subsubcategory = ProductSubSubCategoryListSeializer()
	colour_and_images = SerializerMethodField()
	avg_rating = SerializerMethodField()


	def get_avg_rating(self, instance):
		return round(instance.avg_rating, 1)


	def get_profile_name(self,instance):
		return Profile.objects.filter(user = instance.user).values_list('name',flat=True).first()

	def get_colour_and_images(self,instance):
		qs = instance.available_colours.filter(is_active=True).order_by('special_price')
		if qs.exists():
			data = ColourSizeImageSerializer(qs[0], context = {'type':'web'}).data
			return data
		return {}

	class Meta:
		model = Product
		fields = [
		'id',
		'category',
		'subcategory',
		'subsubcategory',
		'name',
		'avg_rating',
		'qty_sold',
		'main_img',
		'profile_name',
		'colour_and_images'
		]



class ProductReviewsSerializer(ModelSerializer):
	user = UserDetailSerializer()
	class Meta:
		model  = ProductReviews
		fields = [
			'user',
			'rating',
			'content',
			'created'

		]


class ProductAvailablecolourSerializer(ModelSerializer):
	colour = SerializerMethodField()

	def get_colour(self,instance):
	  	return instance.colour.colour

	class Meta:
		model  = ProductAvailableColour
		fields = [
			'colour',
			'init_stock_qty',
			'current_stock_qty',
			'price'

		]

class GetDetailOfProductByColourSerializer(ModelSerializer):

	class Meta:
		model = ProductAvailableColourWithSizeQty
		fields = '__all__'



class ProductColourSerializer(ModelSerializer):
	class Meta:
		model = Colour
		fields = '__all__'


class GetColourWithAvailabilitySerializer(ModelSerializer):
	product_id = SerializerMethodField()
	colour = ProductColourSerializer()

	def get_product_id(self,instance):
		return instance.id

	class Meta:
		model = Product
		fields = ['product_id','colour', 'stock_status']


class GetAvailableColourSerializer(ModelSerializer):
	name = SerializerMethodField()
	colour_code = SerializerMethodField()
	colour_id = SerializerMethodField()
	def get_name(self,instance):
		return instance.colour.name

	def get_colour_code(self,instance):
		return instance.colour.colour_code

	def get_colour_id(self,instance):
		return instance.colour.id
	class Meta:
		model = ProductAvailableColourWithSizeQty
		fields = ['id','colour_id','name','colour_code']


class DetailColourSizeImageSerializer(ModelSerializer):
	product_images = SerializerMethodField()
	available_size = SerializerMethodField()
	total_available_qty  =SerializerMethodField()


	def get_available_size(self,instance):
		sizes = instance.size_and_qty.all()
		qs  = ProductSizeWithQty.objects.filter(id__in = sizes, available_qty__gt = 0).order_by('sort_id')
		data = ProductSizeWithQtySerializer(qs,many=True).data
		return data

	def get_product_images(self,instance):
		print(instance.id , 'sdfsdfsdf')
		qs = ProductImageByColour.objects.filter(product_colour_id = instance.id)

		data = ProductImageByColourSerializer(qs,many=True).data
		return data

	def get_total_available_qty(self,instance):
		total = instance.size_and_qty.all().aggregate(Sum('available_qty'))
		return total['available_qty__sum']
	

	class Meta:
		model = ProductAvailableColourWithSizeQty
		fields = ['id','colour','actual_price','special_price','offer','is_active','product_images','total_available_qty','available_size']


from unity.models import UserBodyMeasurementData

class ProductDetailSerializer(ModelSerializer):
	category = CategoryListSeializer()
	subcategory=SubCategoryListSeializer()
	subsubcategory=SubSubCategoryListSeializer()
	product_reviews = SerializerMethodField()

	usercategory = SerializerMethodField()
	isInwishlist = SerializerMethodField()
	istoken   = SerializerMethodField()
	is_measurement_available = SerializerMethodField()

	colour_and_images = SerializerMethodField()
	available_colours = SerializerMethodField()
	avg_rating = SerializerMethodField()

	def get_is_measurement_available(self, isntance):
		if self.context['request'].user.is_authenticated:
			qs = UserBodyMeasurementData.objects.filter(user=self.context['request'].user)
			if qs.exists():
				return True
		return False

	def get_colour_and_images(self,instance):

		if self.context.get('colour_id') is not None:
			obj = instance.available_colours.filter(id = self.context.get('colour_id')).first()
			print(obj)
			if obj:
				data = DetailColourSizeImageSerializer(obj).data
				return data
		else:
			obj = instance.available_colours.filter(is_active=True).order_by('special_price')
			if obj.exists():
				data = DetailColourSizeImageSerializer(obj[0]).data
				return data
			return {}


	def get_usercategory(self,instance):
		if instance.usercategory is None:
			return None
		return instance.usercategory.name


	def get_product_reviews(self,instance):
		qs = ProductReviews.objects.filter(product=instance.id)
		data = ProductReviewsSerializer(qs,many=True).data
		return data


	def get_isInwishlist(self,instance):
		user_ = self.context['request'].user
		if user_.is_authenticated:
			wishlist = CustomerProductWishList.objects.filter(user = user_, product = instance).exists()
			if wishlist:
				return True
			return False
		return False


	def get_istoken(self,instance):
		user_ = self.context['request'].user
		if user_.is_authenticated:
			return True
		return False


	def get_available_colours(self,instance):
		qs = instance.available_colours.filter(is_active=True)
		data = GetAvailableColourSerializer(qs, many=True).data
		return data

	def get_avg_rating(self, instance):
		return round(instance.avg_rating, 1)

	class Meta:
		model = Product
		fields = [
		'id',
		'category',
		'subcategory',
		'subsubcategory',
		'name',
		'avg_rating',
		'stock_status',
		'total_quantity',
		'description',
		'isfree_delivery',
		'isInwishlist',
		'istoken',
		'available_colours',
		'main_img',
		'material',
		'fit',
		'pattern',
		'fabric',
		'brand',
		'more_info',
		'usercategory',
		'product_reviews',
		'colour_and_images',
		'is_measurement_available',
		]

class Price_DetailSerializer(ModelSerializer):
	class Meta:
		model = ProductAvailableColourWithSizeQty
		fields = ['actual_price','special_price','offer']


class ProductDetailForWishlistSerializer(ModelSerializer):
	price_details = SerializerMethodField()
	made_by   = SerializerMethodField()
	avg_rating = SerializerMethodField()


	def get_avg_rating(self, instance):
		return round(instance.avg_rating, 1)

	def get_price_details(self,instance):
		selected_colour = self.context.get('selected_colour')

		if selected_colour != None and selected_colour!='':
			obj = selected_colour
			data = Price_DetailSerializer(obj).data
			return data
		
		else:
			obj = instance.available_colours.filter(is_active=True).order_by('special_price')
			if obj.exists():
				data = Price_DetailSerializer(obj[0]).data
				return data
			return {}

	def get_made_by(self, instance):
		if instance.user_role=='2':
			return {
				'name':instance.user.first_name,
				'id':instance.user.id
			}
			
		qs = Profile.objects.filter(user=instance.user)
		if qs.exists():
			return {
				'name':qs.first().name,
				'id':qs.first().id
			}

		return ''




	class Meta:
		model = Product
		fields = [
			'id',
			'name',
			'main_img',
			'avg_rating',
			'price_details',
			'user_role',
			'made_by',
		]


class ProductDetailForCartlistSerializer(ModelSerializer):
	price_details = SerializerMethodField()
	main_img  = SerializerMethodField()
	made_by   = SerializerMethodField()
	avg_rating = SerializerMethodField()

	def get_avg_rating(self, instance):
		return round(instance.avg_rating, 1)

	def get_price_details(self,instance):
		selected_colour = self.context.get('selected_colour')

		if selected_colour != None and selected_colour!='':
			obj = selected_colour
			data = Price_DetailSerializer(obj).data
			return data
		
		else:
			obj = instance.available_colours.filter(is_active=True).order_by('special_price')
			if obj.exists():
				data = Price_DetailSerializer(obj[0]).data
				return data
			return {}	

	def get_main_img(self,instance):
		selected_colour = self.context.get('selected_colour')

		if selected_colour != None and selected_colour!='':
			obj = selected_colour
			qs = ProductImageByColour.objects.filter(product_colour_id=selected_colour)
			data = ProductImageByColourSerializer(qs.first()).data			
			return data['image']
		else:
			return instance.main_img

	def get_made_by(self, instance):
		if instance.user_role=='2':
			return instance.user.first_name

		qs = Profile.objects.filter(user=instance.user)
		if qs.exists():
			return qs.first().name
		return ''


	class Meta:
		model = Product
		fields = [
			'id',
			'name',
			'main_img',
			'avg_rating',
			'price_details',
			'user_role',
			'made_by',
		]


class CustomerAllwishListSerializer(ModelSerializer):

	selected_colour = SerializerMethodField()
	selected_size = SerializerMethodField()
	product = ProductDetailForWishlistSerializer()
	stock_msg = SerializerMethodField()

	def get_selected_size(self,instance):
		if instance.selected_size is None:
			return 'Not selected'
		return instance.selected_size

	def get_selected_colour(self,instance):
		if instance.selected_colour is None:
			return 'Not selected'
		return instance.selected_colour.colour.name

	def get_stock_msg(self,instance):

		if instance.product.active == False:
			return 'Out of stock'

		elif instance.product.stock_status == False:
			return 'Out of stock'

		elif not instance.selected_colour == None:
			if not instance.selected_colour.is_active:
				return 'Out of stock'
			return ""
		else:
			return ""

	class Meta:
		model = CustomerProductWishList
		fields = [
			
			'product',
			'selected_colour',
			'selected_size',
			'stock_msg'
		]

class CustomerCartAllProductListSerializer(ModelSerializer):
	product = SerializerMethodField()
	selected_size = SerializerMethodField() 
	selected_colour = SerializerMethodField()
	#edit
	selected_colour_id = SerializerMethodField()
	stock_msg  = SerializerMethodField()

	#----------edit
	def get_selected_colour_id(self, instance):
		return instance.selected_colour.colour.id if instance.selected_colour is not None else 'Not Selected'

	def get_selected_size(self,instance):
		if instance.selected_size is None:
			return 'Not selected'
		return instance.selected_size

	def get_selected_colour(self,instance):
		if instance.selected_colour is None:
			return 'Not selected'
		return instance.selected_colour.colour.name

	def get_product(self,instance):	
		data = ProductDetailForCartlistSerializer(instance.product ,context={'selected_colour':instance.selected_colour}).data	
		return data		

	def get_stock_msg(self,instance):

		qs = instance.selected_colour.size_and_qty.filter(size=instance.selected_size)
		
		if instance.product.active ==False:
			return 'Out of stock'

		elif instance.selected_colour.is_active == False:
			return 'Out of stock'

		elif instance.product.stock_status ==False:
			return 'Out of stock'

		elif not qs.exists():
			return 'Out of stock'

		elif qs.first().available_qty==0:
			return 'Out of stock'

		elif not qs.first().available_qty > instance.selected_quantity:
			return 'Only ' + str(qs.first().available_qty) + ' left'
		else:
			return ''

	class Meta:
		model = CustomerProductCart
		fields = [
			'id',
			'product',
			'selected_size',
			'selected_quantity',
			'selected_colour',
			'stock_msg',
			'selected_colour_id'
		]


class CouponListSerializer(ModelSerializer):
	class Meta:
		model = CouponCode
		fields = ['id','code','description','terms_and_cond']




from .import models
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['username','email']
class HybridImageField(serializers.ImageField):
    """A flexible field that accepts either an image file or a remote URL string."""

    def to_internal_value(self, data):
        # If it’s a string starting with http(s), treat as URL
        if isinstance(data, str) and (data.startswith('http') or data.startswith('https')):
            return data
        # Otherwise, process as a normal uploaded file
        return super().to_internal_value(data) 
    
class PostSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    featured_image = HybridImageField(required=False, allow_null=True)

    class Meta:
        model = models.Post
        fields = ['id', 'author', 'title', 'slug', 'excerpt', 'content', 'featured_image']
    
class ContactMessageSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    class Meta:
        model = models.ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message','phone', 'created_at']
class CategorySerializer1(serializers.ModelSerializer):
    class Meta:
        model = models.Category1
        fields = ['id', 'name']
        
class CauseSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=models.Category1.objects.all()
    )
    image = serializers.ReadOnlyField()  # unified output (from model property)

    class Meta:
        model = models.Cause
        fields = [
            'id',
            'title',
            'category',
            'goal_amount',
            'featured',
            'image_file',         
            'image_url', 
            'image',         
            'short_description',
            'full_content',
        ]
        read_only_fields = ['image']

    def validate(self, data):
        request = self.context.get('request')

        # Accept frontend key 'image' as alias
        image_file = (
            data.get('image_file')
            or (request and request.FILES.get('image_file'))
            or (request and request.FILES.get('image'))
        )
        image_url = (
            data.get('image_url')
            or data.get('image')
            or (request and request.data.get('image_url'))
            or (request and request.data.get('image'))
        )

        if not image_file and not image_url:
            raise serializers.ValidationError(
                {"non_field_errors": ["Please provide either an image file or an image URL."]}
            )

        data['image_file'] = image_file
        data['image_url'] = image_url
        return data


class TestimonialSerializer(serializers.ModelSerializer):
    image = serializers.ReadOnlyField()  # use model's @property

    class Meta:
        model = models.Testimonial
        fields = ['id', 'name', 'role', 'rating', 'image', 'content']

    def validate(self, data):
        request = self.context.get('request')

    # Try all possible keys (image_file, image_url, image)
    
        image_file = (
            data.get('image_file') or
            (request and request.FILES.get('image_file')) or
             (request and request.FILES.get('image'))
             )
        image_url = (
            data.get('image_url') or
            data.get('image') or
            (request and request.data.get('image_url')) or
             (request and request.data.get('image'))
            )

        if not image_file and not image_url:
            raise serializers.ValidationError(
                 {"non_field_errors": ["Please provide either an image file or an image URL."]}
               )

    # Assign them properly for saving
        data['image_file'] = image_file
        data['image_url'] = image_url
        return data


        
class VolunteerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    availability = serializers.ChoiceField(choices=models.volunteer.AVAILABILITY_CHOICES, required=True)
    class Meta:
        model = models.volunteer
        fields = ['full_name', 'age', 'email', 'phone', 'address', 'occupation', 'availability', 'skills', 'reason']

from rest_framework import serializers
from .models import Gallary, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class GallarySerializer(serializers.ModelSerializer):
    category_name = serializers.SlugRelatedField(
        slug_field='name',  # accept category name like "Cows"
        queryset=Category.objects.all()
    )
    image = HybridImageField(required=False, allow_null=True)
    class Meta:
        model = Gallary
        fields = ['id', 'image', 'category_name', 'caption']

    def to_internal_value(self, data):
        """Allow both uploaded files and URL strings for image."""
        ret = super().to_internal_value(data)
        request = self.context.get('request')

        # Handle uploaded file
        if request and 'image' in request.FILES:
            ret['image'] = request.FILES['image']

        # Handle URL string
        elif isinstance(data.get('image'), str):
            image_str = data.get('image')
            if image_str.startswith('http'):
                ret['image'] = image_str  # accept image URL

        return ret

class ProgramSerializer(serializers.ModelSerializer):
    file_image = serializers.ImageField(required=False, allow_null=True)
    url_image = serializers.URLField(required=False, allow_null=True)
    image = serializers.ReadOnlyField()  # unified output

    class Meta:
        model = models.Program
        fields = ['id', 'title', 'description', 'file_image', 'url_image', 'image']
        read_only_fields = ['image']

    def validate(self, data):
        request = self.context.get('request')

        file_image = (
            data.get('file_image')
            or (request and request.FILES.get('file_image'))
        )
        url_image = (
            data.get('url_image')
            or (request and request.data.get('url_image'))
        )

        if not file_image and not url_image:
            raise serializers.ValidationError(
                {"non_field_errors": ["Please provide either a file image or a URL image."]}
            )

        data['file_image'] = file_image
        data['url_image'] = url_image
        return data

User = get_user_model()
 
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    This overrides SimpleJWT's TokenObtainPairSerializer to authenticate by username.
    """
    username_field = 'username'   
    def validate(self, attrs):   
        username = attrs.get('username')
        password = attrs.get('password')   
        if not username or not password:
            raise serializers.ValidationError('Username and password are required.')        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid username or password.')      
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid username or password.')      
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')       
        data = super().validate(attrs)   
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_superuser': user.is_superuser,
        }
        return data
    
    



from rest_framework import serializers
from . import models


class DonationSerializer(serializers.ModelSerializer):

    final_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True   
    )

    class Meta:
        model = models.Donation
        fields = '__all__'

    def validate(self, data):
        selected = data.get("selected_amount")
        custom = data.get("custom_amount")

        if not selected and not custom:
            raise serializers.ValidationError("Provide amount")

        if selected and custom:
            raise serializers.ValidationError("Only one amount allowed")

        return data
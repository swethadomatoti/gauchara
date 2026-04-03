from .import models
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CloudinaryURLField(serializers.Field):
    """Serializer field for CloudinaryField that returns full URL"""
    def to_representation(self, value):
        if not value:
            return None
        # CloudinaryField returns a FieldFile object with .url property
        if hasattr(value, 'url'):
            return value.url
        # Fallback: build URL from public ID if needed
        return f"https://res.cloudinary.com/dmxfdt7ub/image/upload/{str(value)}" if value else None
    
    def to_internal_value(self, data):
        return data

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['username','email']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token

class PostSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    featured_image = CloudinaryURLField(required=False, allow_null=True)

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
    image = serializers.ReadOnlyField()
    image_file = CloudinaryURLField(required=False, allow_null=True)

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
    # Incoming payload may provide image via this alias.
    # Writes to image_url field and still allows image_file uploads.
    image = serializers.URLField(source='image_url', required=False, allow_null=True)
    image_file = CloudinaryURLField(required=False, allow_null=True)

    class Meta:
        model = models.Testimonial
        fields = ['id', 'name', 'role', 'rating', 'image', 'image_file', 'image_url', 'content']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Legacy fallback: if image_url is empty and image_file exists in DB
        if not data.get('image') and instance.image_file:
            data['image'] = str(instance.image_file)
        return data

    def validate(self, data):
        # Accept both image and image_url keys in input.
        image_url = data.get('image_url') or data.get('image_file') and None
        image_file = data.get('image_file')

        # If the client sent "image" as alias for URL, ModelSerializer source handles it.
        # No strict requirement here to allow partial data.

        # If image_url and image_file both missing, keep null (optional field)
        # for backward compatibility and value injection.

        return data

        
class VolunteerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    availability = serializers.ChoiceField(choices=models.volunteer.AVAILABILITY_CHOICES, required=True)
    class Meta:
        model = models.volunteer
        fields = ['id','full_name', 'age', 'email', 'phone', 'address', 'occupation', 'availability', 'skills', 'reason']

from rest_framework import serializers
from .models import Gallary, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class GallarySerializer(serializers.ModelSerializer):
    category_name = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all()
    )
    image = CloudinaryURLField(required=False, allow_null=True)
    
    class Meta:
        model = Gallary
        fields = ['id', 'image', 'category_name', 'caption']


class ProgramSerializer(serializers.ModelSerializer):
    file_image = CloudinaryURLField(required=False, allow_null=True)
    
    class Meta:
        model = models.Program
        fields = ['id', 'title', 'description', 'file_image', 'url_image', 'created_at']


class DonationSerializer(serializers.ModelSerializer):
    uploaded_receipt = CloudinaryURLField(required=True, allow_null=True)
    
    class Meta:
        model = models.Donation
        fields = [
            'id', 'full_name', 'email', 'whatsapp_number', 'pan_number',
            'selected_amount', 'custom_amount', 'final_amount', 'region',
            'uploaded_receipt', 'payment_status', 'created_at'
        ]
        read_only_fields = ['id', 'final_amount', 'payment_status', 'created_at']

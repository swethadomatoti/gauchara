from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.text import slugify

class CustomUser(AbstractUser):
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(max_length=150,unique=True,validators=[username_validator],
                                error_messages={'unique': 'A user with that username already exists.'},
                                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                verbose_name='username')

class Post(models.Model):
    author = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField()
    # Hybrid field — can store upload file path or remote URL string
    featured_image = models.ImageField(upload_to='uploads/', blank=True, null=True,max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically generate unique slugs"""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        """Return full URL for uploaded or remote images."""
        if not self.featured_image:
            return None
        image_str = str(self.featured_image)
        # Return remote URLs directly (Google, CDN, etc.)
        if image_str.startswith('http'):
            return image_str
        # Return local uploaded image via MEDIA_URL
        return f"/media/{image_str}"
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)   
    email = models.EmailField()             
    subject = models.CharField(max_length=200)   
    message = models.TextField()
    phone = models.CharField(max_length=15, blank=False, null=True)          
    created_at = models.DateTimeField(auto_now_add=True)  
     

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
class Category1(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Cause(models.Model): 
    title = models.CharField(max_length=200)
    category = models.ForeignKey('Category1', on_delete=models.CASCADE)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    featured = models.BooleanField(default=False)
    image_file = models.ImageField(upload_to='uploads/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    short_description = models.CharField(max_length=255)
    full_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def image(self):
        """
        Unified image property: returns either the uploaded file's URL or the remote URL.
        """
        if self.image_url:
            # If a remote URL was provided
            return self.image_url
        elif self.image_file:
            # If a local file was uploaded
            return f"/media/{self.image_file}"
        return None


class Testimonial(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    rating = models.IntegerField(choices=RATING_CHOICES)
    image_file = models.ImageField(upload_to='uploads/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def image(self):
        """
        Unified image property: returns either the uploaded file's URL or the remote URL.
        """
        if self.image_url:
            # If a remote URL was provided
            return self.image_url
        elif self.image_file:
            # If a local file was uploaded
            return f"/media/{self.image_file}"
        return None
    
class volunteer(models.Model):
    AVAILABILITY_CHOICES = [
        ('WEEKDAYS', 'Weekdays'),
        ('WEEKENDS', 'Weekends'),
        ('BOTH', 'Both Weekdays and Weekends'),
        ('FLEXIBLE', 'Flexible'),
        ]
    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    occupation = models.CharField(max_length=100)
    availability = models.CharField(max_length=100, choices=AVAILABILITY_CHOICES)
    skills = models.CharField(max_length=255)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Gallary(models.Model):   
       
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    category_name = models.ForeignKey(Category, on_delete=models.CASCADE)
    caption = models.CharField(max_length=255, blank=True, null=True)
    @property
    def image_url(self):
        """Return the correct URL for the image."""
        if not self.image:
            return None

        # If it's a full URL, return as-is
        if str(self.image).startswith('http'):
            return self.image

        # Otherwise, serve it as a media file
        return f"/media/{self.image}"

class Program(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file_image =models.ImageField(upload_to='uploads/', blank=True, null=True)
    url_image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Donation(models.Model):

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)

    selected_amount = models.IntegerField(
        choices=[
            (500, "₹500"),
            (1000, "₹1000"),
            (2500, "₹2500"),
            (5000, "₹5000"),
            (10000, "₹10000"),
            (25000, "₹25000"),
        ],
        blank=True,
        null=True
    )

    custom_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    region = models.CharField(choices=[('India', 'India'), ('International', 'International')], max_length=20)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    uploaded_receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'pending'),
            ('success', 'success'),
            ('failed', 'failed')
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
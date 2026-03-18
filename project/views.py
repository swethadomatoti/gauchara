from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib.auth import authenticate, login ,logout
from rest_framework_simplejwt.tokens import RefreshToken
import json
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication  
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny ,IsAdminUser
from .models import Post, ContactMessage , Cause, Program , Testimonial, volunteer, Category , Gallary , Category1 , Donation
from .serializers import CustomTokenObtainPairSerializer,PostSerializer, ContactMessageSerializer ,CauseSerializer, ProgramSerializer, TestimonialSerializer, VolunteerSerializer , CategorySerializer , GallarySerializer , CategorySerializer1,DonationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.conf import settings
from .task import send_contact_email, send_donation_email, send_volunteer_email


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


User = get_user_model()
@csrf_exempt
def login_user(request):
    # Allow only POST method
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Get username and password from JSON
    username = data.get('username')
    password = data.get('password')

    # Check if both fields are provided
    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)

    # Authenticate user (no need to fetch user manually)
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    # Log the user in (creates session)
    login(request, user)

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)

    # Return response
    return JsonResponse({
        "message": f"Login successful! Welcome, {user.get_full_name()}",
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "refresh": str(refresh),
        "access": access
    }, status=200)
    
@csrf_exempt
def logout_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        refresh_token = data.get("refresh")
    except Exception:
        refresh_token = None
    logout(request)
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()   
        except TokenError:
            return JsonResponse({"error": "Invalid or expired refresh token."}, status=400)
        except Exception:
            return JsonResponse({"error": "Logout failed while blacklisting token."}, status=400)
    return JsonResponse({"message": "Logged out successfully."}, status=200)


class BlogView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk=None):
        if pk:
            try:
                post = Post.objects.get(pk=pk)
            except Post.DoesNotExist:
                return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data)
        else:
            posts = Post.objects.all().order_by('-created_at')
            serializer = PostSerializer(posts, many=True, context={'request': request})
            return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Only admin can create posts'}, status=status.HTTP_403_FORBIDDEN)

      
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({'error': 'Only admin can update posts'}, status=status.HTTP_403_FORBIDDEN)
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        
        serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'error': 'Only admin can delete posts'}, status=status.HTTP_403_FORBIDDEN)
        try:
            post = Post.objects.get(pk=pk)
            post.delete()
            return Response({'message': 'Post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
 
@method_decorator(csrf_exempt, name='dispatch')
class ContactMessageView(APIView):

    def get(self, request):
        messages = ContactMessage.objects.all().order_by('-created_at')  # latest first
        serializer = ContactMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)

        if serializer.is_valid():
            message = serializer.save()   # save message in database
            # trigger celery email task
            send_contact_email(
            message.name,
            message.email,
            message.phone,
            message.subject,
            message.message
              )

            return Response(
            {"message": "Thank you for contacting us! We'll get back to you soon."},
            status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        try:
            message = ContactMessage.objects.get(pk=pk)
            message.delete()
            return Response({'message': 'Message deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

class Category1View(APIView):
    def get(self, request):
        categories = Category1.objects.all()
        serializer = CategorySerializer1(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = CategorySerializer1(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        try:
            category_instance = Category1.objects.get(pk=pk)
            category_instance.delete()
            return Response({"message": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Category1.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
@method_decorator(csrf_exempt, name='dispatch')
class CauseView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                cause = Cause.objects.get(pk=pk)
            except Cause.DoesNotExist:
                return Response({"error": "Cause not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = CauseSerializer(cause, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            causes = Cause.objects.all().order_by('-created_at')
            serializer = CauseSerializer(causes, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CauseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Cause created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            cause = Cause.objects.get(pk=pk)
        except Cause.DoesNotExist:
            return Response({"error": "Cause not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CauseSerializer(cause, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Cause updated successfully!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            cause = Cause.objects.get(pk=pk)
            cause.delete()
            return Response({"message": "Cause deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Cause.DoesNotExist:
            return Response({"error": "Cause not found."}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class TestimonialView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                testimonial = Testimonial.objects.get(pk=pk)
            except Testimonial.DoesNotExist:
                return Response({"error": "Testimonial not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = TestimonialSerializer(testimonial, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            testimonials = Testimonial.objects.all().order_by('-created_at')
            serializer = TestimonialSerializer(testimonials, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TestimonialSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Testimonial created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            testimonial = Testimonial.objects.get(pk=pk)
        except Testimonial.DoesNotExist:
            return Response({"error": "Testimonial not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TestimonialSerializer(testimonial, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Testimonial updated successfully!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            testimonial = Testimonial.objects.get(pk=pk)
            testimonial.delete()
            return Response({"message": "Testimonial deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Testimonial.DoesNotExist:
            return Response({"error": "Testimonial not found."}, status=status.HTTP_404_NOT_FOUND)
        
class VolunteerView(APIView):
    def get(self, request):
        volunteers = volunteer.objects.all().order_by('-created_at')
        serializer = VolunteerSerializer(volunteers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = VolunteerSerializer(data=request.data)

        if serializer.is_valid():
            volunteer = serializer.save()

            # Send email to admin
            send_volunteer_email(
                volunteer.full_name,
                volunteer.age,
                volunteer.email,
                volunteer.phone,
                volunteer.address,
                volunteer.occupation,
                volunteer.availability,
                volunteer.skills,
                volunteer.reason
            )

            return Response(
                {"message": "Thank you for volunteering! We'll be in touch soon."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        try:
            volunteer_instance = volunteer.objects.get(pk=pk)
            volunteer_instance.delete()
            return Response({"message": "Volunteer application deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except volunteer.DoesNotExist:
            return Response({"error": "Volunteer application not found."}, status=status.HTTP_404_NOT_FOUND)

class CategoryView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        try:
            category_instance = Category.objects.get(pk=pk)
            category_instance.delete()
            return Response({"message": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
class GallaryView(APIView):
    def get(self, request):
        gallary_items = Gallary.objects.all()
        serializer = GallarySerializer(gallary_items, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GallarySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Gallery item created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            gallary_item = Gallary.objects.get(pk=pk)
        except Gallary.DoesNotExist:
            return Response({"error": "Gallery item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GallarySerializer(gallary_item, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Gallery item updated successfully!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            gallary_item = Gallary.objects.get(pk=pk)
            gallary_item.delete()
            return Response({"message": "Gallery item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Gallary.DoesNotExist:
            return Response({"error": "Gallery item not found."}, status=status.HTTP_404_NOT_FOUND)

class ProgramView(APIView):
    def get(self,request,pk=None):
        if pk:
            try:
                program =Program.objects.get(pk=pk)
            except Program.DoesNotExist:
                return Response({"error": "Program not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = ProgramSerializer(program, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK) 
        else:
            programs=Program.objects.all().order_by('-created_at')
            serializer=ProgramSerializer(programs,many=True,context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self,request):
        serializer=ProgramSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Program created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self,request,pk):
        try:
            program =Program.objects.get(pk=pk)
        except Program.DoesNotExist:
            return Response({"error": "Program not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer=ProgramSerializer(program,data=request.data,partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Program updated successfully!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        try:
            program=Program.objects.get(pk=pk)
            program.delete()
            return Response({"message": "Program deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Program.DoesNotExist:
            return Response({"error": "Program not found."}, status=status.HTTP_404_NOT_FOUND)


class DonationCreateView(APIView):

    permission_classes = [AllowAny]    

    def post(self, request):

        serializer = DonationSerializer(data=request.data)

        if serializer.is_valid():

            selected = serializer.validated_data.get("selected_amount")
            custom = serializer.validated_data.get("custom_amount")

            final_amount = custom if custom else selected
            donation = serializer.save(
                final_amount=final_amount,
                payment_status="pending"   
            )

            return Response(
                {"message": "Donation submitted. Waiting for approval"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class DonationListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]   #  only admin

    def get(self, request):

        donations = Donation.objects.all().order_by('-created_at')

        serializer = DonationSerializer(donations, many=True)

        return Response(serializer.data)

class DonationStatusUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):

        try:
            donation = Donation.objects.get(pk=pk)
        except Donation.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        new_status = request.data.get("payment_status")

        if new_status not in ["pending", "success", "failed"]:
            return Response({"error": "Invalid status"}, status=400)

        donation.payment_status = new_status
        donation.save()

        if new_status in ["success", "failed"]:
            send_donation_email(
                donation.full_name,
                donation.email,
                donation.whatsapp_number,
                donation.final_amount,
                donation.payment_id,
                donation.payment_status
            )

        return Response({"message": "Status updated"})
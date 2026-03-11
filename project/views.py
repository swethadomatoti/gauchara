from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib.auth import authenticate, login ,logout
from rest_framework_simplejwt.tokens import RefreshToken
import json
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication  
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from .models import Post, ContactMessage , Cause, Program , Testimonial, volunteer, Category , Gallary , Category1 , Donation
from .serializers import CustomTokenObtainPairSerializer,PostSerializer, ContactMessageSerializer ,CauseSerializer, ProgramSerializer, TestimonialSerializer, VolunteerSerializer , CategorySerializer , GallarySerializer , CategorySerializer1
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.conf import settings
import razorpay
import paypalrestsdk
import qrcode
from io import BytesIO
from .utils import generate_upi_link

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
            serializer.save()
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
            serializer.save()
            return Response({"message": "Thank you for volunteering! We'll be in touch soon."}, status=status.HTTP_201_CREATED)
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
   
        
# #-------------------------------------------------------------------------------------------------------------------------------------------------------
#  #PAYMENT GATEWAYS
# #----------------------------------------------------------------------------------------------------

# # ------------------- RAZORPAY -------------------
# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# @csrf_exempt
# def create_razorpay_order(request):
#     """Create Razorpay order for donation"""
#     if request.method != "POST":
#         return HttpResponseBadRequest("POST required")
    
#     data = json.loads(request.body)
#     donor_name = data.get("donor_name")
#     donor_email = data.get("donor_email")
#     amount = float(data.get("amount", 500))  # in INR

#     if not donor_name or not donor_email:
#         return JsonResponse({"error": "Missing donor name or email"}, status=400)

#     amount_paise = int(amount * 100)  # Razorpay expects amount in paise

#     # Create Razorpay order
#     razorpay_order = razorpay_client.order.create({
#         "amount": amount_paise,
#         "currency": "INR",
#         "payment_capture": 1
#     })

#     # Save donation as pending
#     donation = Donation.objects.create(
#         donor_name=donor_name,
#         donor_email=donor_email,
#         amount=amount,
#         payment_method="Razorpay",
#         payment_status="Pending",
#         transaction_id=razorpay_order['id']
#     )

#     return JsonResponse({
#         "order_id": razorpay_order['id'],
#         "amount": amount_paise,
#         "currency": "INR",
#         "donation_id": donation.id,
#         "key": settings.RAZORPAY_KEY_ID
#     })


# @csrf_exempt
# def razorpay_webhook(request):
#     """Webhook to verify Razorpay payments"""
#     signature = request.headers.get("X-Razorpay-Signature")
#     body = request.body
#     webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET

#     # Verify Razorpay webhook signature
#     try:
#         razorpay_client.utility.verify_webhook_signature(body, signature, webhook_secret)
#     except razorpay.errors.SignatureVerificationError:
#         return HttpResponse(status=400)

#     event = json.loads(body)
#     if event.get("event") == "payment.captured":
#         payment_entity = event["payload"]["payment"]["entity"]
#         try:
#             donation = Donation.objects.get(transaction_id=payment_entity["order_id"])
#             donation.payment_status = "Success"
#             donation.transaction_id = payment_entity["id"]
#             donation.save()
#         except Donation.DoesNotExist:
#             return HttpResponse(status=404)

#     return HttpResponse(status=200)


# # ------------------- PAYPAL -------------------
# paypalrestsdk.configure({
#     "mode": settings.PAYPAL_MODE,
#     "client_id": settings.PAYPAL_CLIENT_ID,
#     "client_secret": settings.PAYPAL_CLIENT_SECRET
# })

# @csrf_exempt
# def create_paypal_payment(request):
#     """Create PayPal payment for donation"""
#     data = json.loads(request.body)
#     donor_name = data.get("donor_name")
#     donor_email = data.get("donor_email")
#     amount = str(data.get("amount", 500))

#     if not donor_name or not donor_email:
#         return JsonResponse({"error": "Missing donor name or email"}, status=400)

#     # Save donation as pending
#     donation = Donation.objects.create(
#         donor_name=donor_name,
#         donor_email=donor_email,
#         amount=float(amount),
#         payment_method="PayPal",
#         payment_status="Pending"
#     )

#     payment = paypalrestsdk.Payment({
#         "intent": "sale",
#         "payer": {"payment_method": "paypal"},
#         "redirect_urls": {
#             "return_url": f"https://yourdomain.com/paypal-success/{donation.id}/",
#             "cancel_url": f"https://yourdomain.com/paypal-cancel/{donation.id}/"
#         },
#         "transactions": [{
#             "amount": {"total": amount, "currency": "INR"},
#             "description": f"Donation to GauChara: {donation.id}"
#         }]
#     })

#     if payment.create():
#         approval_url = [link.href for link in payment.links if link.rel == "approval_url"][0]
#         return JsonResponse({"approval_url": approval_url})
#     else:
#         return JsonResponse({"error": payment.error})


# # ------------------- UPI QR -------------------
# @csrf_exempt
# def upi_qr_code(request):
#     """Generate dynamic QR code for UPI payments"""
#     donor_name = request.GET.get("donor_name")
#     upi_id = request.GET.get("upi_id")
#     amount = request.GET.get("amount")

#     if not donor_name or not upi_id or not amount:
#         return JsonResponse({"error": "Missing required parameters"}, status=400)

#     try:
#         amount = float(amount)
#     except ValueError:
#         return JsonResponse({"error": "Invalid amount"}, status=400)

#     upi_link = generate_upi_link(donor_name, upi_id, amount)

#     qr = qrcode.QRCode(version=1, box_size=10, border=5)
#     qr.add_data(upi_link)
#     qr.make(fit=True)
#     img = qr.make_image(fill_color="black", back_color="white")

#     buffer = BytesIO()
#     img.save(buffer, format="PNG")
#     buffer.seek(0)

#     return HttpResponse(buffer.getvalue(), content_type="image/png")


# @csrf_exempt
# def create_upi_donation(request):
#     """Create a donation record for QR-UPI"""
#     if request.method != "POST":
#         return JsonResponse({"error": "POST method required"}, status=400)

#     data = json.loads(request.body)
#     donor_name = data.get("donor_name")
#     donor_email = data.get("donor_email")
#     amount = data.get("amount", 500)

#     if not donor_name or not donor_email:
#         return JsonResponse({"error": "Missing donor name or email"}, status=400)

#     donation = Donation.objects.create(
#         donor_name=donor_name,
#         donor_email=donor_email,
#         amount=float(amount),
#         payment_method="QR-UPI",
#         payment_status="Pending"
#     )

#     return JsonResponse({
#         "donation_id": donation.id,
#         "message": "Donation created. Now scan QR to pay."
#     })
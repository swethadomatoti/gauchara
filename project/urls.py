from django.urls import path
from .import views
from .views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('blog/',views.BlogView.as_view(),name='blog'),
    path('blog/<int:pk>/',views.BlogView.as_view(),name='blog-detail'),
    path('contact/',views.ContactMessageView.as_view(),name='contact'),
    path('contact/<int:pk>/',views.ContactMessageView.as_view(),name='contact-detail'),
    path('category1/',views.Category1View.as_view(),name='category1'),
    path('category1/<int:pk>/',views.Category1View.as_view(),name='category1-detail'),
    path('cause/',views.CauseView.as_view(),name='cause'),
    path('cause/<int:pk>/',views.CauseView.as_view(),name='cause-detail'),
    path('testimonial/',views.TestimonialView.as_view(),name='testimonial'),
    path('testimonial/<int:pk>/',views.TestimonialView.as_view(),name='testimonial-detail'),
    path('volunteer/',views.VolunteerView.as_view(),name='volunteer'),
    path('volunteer/<int:pk>/',views.VolunteerView.as_view(),name='volunteer-detail'),
    path('category/',views.CategoryView.as_view(),name='category'),
    path('category/<int:pk>/',views.CategoryView.as_view(),name='category-detail'),
    path('gallery/',views.GallaryView.as_view(),name='gallery'),
    path('gallery/<int:pk>/',views.GallaryView.as_view(),name='gallery-detail'),
    path('program/',views.ProgramView.as_view(),name='program'),
    path('program/<int:pk>/',views.ProgramView.as_view(),name='program-detail'),
    path('donation1/',views.DonationCreateView.as_view(),name='donation'),
    path('donation2/',views.DonationListView.as_view(),name='donation-list'),
    path('donation3/<int:pk>/status/',views.DonationStatusUpdateView.as_view(),name='donation-status-update'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),       
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),  
]

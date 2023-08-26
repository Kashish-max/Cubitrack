from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import SignupView, LoginView, VerifyEmailView, ResendVerificationLinkView

urlpatterns = [
    # default login endpoint provided by DRF (uses username and password)
    path('token/', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
    # Refreshes the access token provided in the authorization header
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),

    # Cussom endpoints
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'), 
    path('resend-verification/', ResendVerificationLinkView.as_view(), name='resend-verification'),

    # custom login endpoint (uses email and password)
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', jwt_views.TokenBlacklistView.as_view(), name ='logout')
]
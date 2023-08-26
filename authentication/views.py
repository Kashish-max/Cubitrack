import uuid
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.mail import send_mail
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import token_blacklist
from rest_framework import status

from .serializers import SignupSerializer, LoginSerializer

User = get_user_model()


def send_sendgrid_verification_email(user, verification_url):
    message = Mail(
        from_email='Cubitrack <kashish.smtp@gmail.com>',
        to_emails=user.email
    )

    message.dynamic_template_data = {
        'verification_url': verification_url,
    }
    message.template_id = settings.SENDGRID_TEMPLATE
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    response = sg.send(message)
    return str(response.status_code)

def send_verification_email(user, verification_url):
    from_email = "Cubitrack <noreply@cubitrack.com>"
    message = f'Click the link to verify your email: {verification_url}\n\nThis link will expire in 20 minutes. If you did not request this, you can disregard this email.\n\nSincerely,\nCubitrack'
    send_mail('Cubitrack account email verification.', message, from_email, [user.email], fail_silently=False)


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                existing_user = User.objects.get(
                    Q(email=serializer.validated_data["email"]) | Q(username=serializer.validated_data["username"])
                )
                response = "A user with that username or email already exists."
                return Response({"error": response}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                try:
                    user = User.objects.create_user(**serializer.validated_data)
                    verification_link = reverse('verify-email', args=[user.verification_token])
                    verification_url = f'{settings.EMAIL_VERIFICATION_DOMAIN}{verification_link}'
                    try:
                        send_sendgrid_verification_email(user, verification_url) # Send verification email
                    except Exception as e:
                        send_verification_email(user, verification_url)  # Send verification email
                    return Response({"message": "User registered. A verification link has been sent to your email."}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    user.delete()
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
            token_age = timezone.now() - user.token_created_at
            token_expiry_duration = timedelta(minutes=20)  # Token expires in 20 minutes

            if token_age <= token_expiry_duration:
                user.email_verified = True
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Verification link has expired. Please request a new link."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "Invalid verification token."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                if user.email_verified:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "refresh": str(refresh),
                        "access": str(refresh.access_token)
                    }, status=status.HTTP_200_OK)
                else:
                    resend_view = ResendVerificationLinkView()
                    response = resend_view.post(request)
                    return response
            else:
                return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationLinkView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        try:
            user = User.objects.get(email=email)

            # validating again in case request is made separately to resend verification route instead of login route
            if user.check_password(password):
                if not user.email_verified:
                    self.send_verification_email(user)
                    return Response({"message": "New verification link sent."}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Email already verified."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"message": "User with this email not found."}, status=status.HTTP_404_NOT_FOUND)

    def send_verification_email(self, user):
        user.verification_token = uuid.uuid4()
        user.token_created_at = timezone.now()
        user.save()

        verification_link = reverse('verify-email', args=[user.verification_token])
        verification_url = f'{settings.EMAIL_VERIFICATION_DOMAIN}{verification_link}'
        try:
            send_sendgrid_verification_email(user, verification_url) # Send verification email
        except Exception as e:
            send_verification_email(user, verification_url)  # Send verification email
        return Response({"message": "Check your email for verification."}, status=status.HTTP_200_OK)

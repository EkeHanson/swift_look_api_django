from rest_framework.permissions import AllowAny
from .serializers import CustomUserSerializer, LoginSerializer
from rest_framework import status, generics, viewsets, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomUserSerializer, ResetPasswordSerializer
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

import requests
from django.http import JsonResponse
from django.conf import settings
from django.views import View
from django.utils.decorators import method_decorator


@method_decorator(permission_classes([AllowAny]), name='dispatch')
class IPGeoLocationView(View):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        # Get IP address from query parameter or use default (client IP)
        ip_address = request.GET.get('ip', request.META.get('REMOTE_ADDR'))
        
        # MaxMind API URL with the IP address as a parameter
        maxmind_url = f"https://geoip.maxmind.com/geoip/v2.1/city/{ip_address}"
        
        # Your MaxMind license key
        #license_key = settings.MAXMIND_LICENSE_KEY  # Store license key in settings for security
        license_key = 'django-insecure-48kh6q*a6*mo2b#6j3)*-8_x)t54q2yd2zs78nchnfz4dq^jyi'  # Store license key in settings for security
        
        # Make the API request with basic authentication
        response = requests.get(maxmind_url, auth=(license_key, ''))
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse and return the JSON response
            location_data = response.json()
            return JsonResponse({
                'ip': ip_address,
                'city': location_data['city']['names']['en'],
                'country': location_data['country']['names']['en'],
                'latitude': location_data['location']['latitude'],
                'longitude': location_data['location']['longitude'],
                'region': location_data['subdivisions'][0]['names']['en']
            })
        else:
            # Handle errors if the request fails
            return JsonResponse({'error': 'Failed to retrieve location data'}, status=response.status_code)


class CustomUserViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all().order_by('id') 
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        # Get the IP address from the request
        user_ip = request.META.get('REMOTE_ADDR')

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        user.created_ip = user_ip  # Save the IP address
        user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate the input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated email and password
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Authenticate user using email and password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            # Return tokens and user details on successful login
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'email': user.email,
                'user_type': user.user_type,
                'userId': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined,
                'unique_user_id': user.unique_user_id,
            }, status=status.HTTP_200_OK)

        # Return error if authentication fails
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_contact_email(request):
    email = request.data.get('email')
    full_name = request.data.get('full_name')
    subject = request.data.get('subject')
    message_body = request.data.get('message')

    if email:
        subject_line = f"New Contact Message: {subject}"
        message = f'''
        <html>
        <body>
            <h3>Contact Form Submission</h3>
            <p><strong>Full Name:</strong> {full_name}</p>
            <p><strong>Email Address:</strong> {email}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Message:</strong> {message_body}</p>
        </body>
        </html>
        '''
        recipient_list = ['ekenehanson@gmail.com']
        from_email = 'ekenehanson@sterlingspecialisthospitals.com'

        send_mail(subject_line, '', from_email, recipient_list, fail_silently=False, html_message=message)
        
        return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
    
    return Response({'error': 'Email not provided in POST data'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        # Check if email is provided
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Find user with provided email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Generate reset token and UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"https://swiftlookv1.vercel.app/forgotten_pass_reset/{uid}/{token}/"

        # Prepare email content
        subject = 'Password Reset Request'

        # Use a proper HTML template for the message
        message = f"Please click the following link to reset your password: {reset_link}"
        html_message = f'''
            <html>
                <body>
                    <h3>Please click on the link below to reset your password</h3>
                    <p><a href="{reset_link}"><strong>Reset Password</strong></a></p>
                    <p> Note this email will expire in five (5) minutes. </p>
                </body>
            </html>
        '''

        from_email = 'ekenehanson@sterlingspecialisthospitals.com'
        recipient_list = [email]

        # Send the email with the HTML content
        send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

        return Response({'message': 'Password reset link has been sent to your email'}, status=status.HTTP_200_OK)

class ConfirmResetPasswordView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token, *args, **kwargs):

        serializer = ResetPasswordSerializer(data=request.data)

        # Validate the serializer
        if not serializer.is_valid():
            # print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Token is valid; proceed with password reset
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)


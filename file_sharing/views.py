from django.shortcuts import render

# Create your views here.
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import User, UploadedFile, EmailVerification, SecureDownloadURL
from .serializers import UserSignUpSerializer, UserLoginSerializer, FileUploadSerializer, UploadedFileSerializer
from .utils import encrypt_url, decrypt_url
import uuid
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Welcome to the File Sharing API"})

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """Client user signup with encrypted URL return"""
    serializer = UserSignUpSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Create email verification token
        verification = EmailVerification.objects.create(user=user)
        
        # Send verification email (in production, use proper email service)
        verification_url = f"http://localhost:8000/api/verify-email/{verification.token}/"
        
        # For development, we'll use console backend
        send_mail(
            'Verify Your Email',
            f'Click here to verify your email: {verification_url}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        response_data = {
            'message': 'User created successfully',
            'user_id': user.id,
            'email': user.email,
        }
        
        # Return encrypted URL for client users
        if user.user_type == 'client':
            response_data['encrypted_url'] = user.encrypted_signup_url
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email(request, token):
    """Email verification endpoint"""
    try:
        verification = EmailVerification.objects.get(token=token, is_verified=False)
        
        if verification.is_expired():
            return Response({'error': 'Verification link has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        verification.user.is_email_verified = True
        verification.user.save()
        
        verification.is_verified = True
        verification.save()
        
        return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
    
    except EmailVerification.DoesNotExist:
        return Response({'error': 'Invalid verification token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """Login for both ops and client users"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        return Response({
            'access_token': access_token,
            'refresh_token': str(refresh),
            'user_type': user.user_type,
            'email': user.email,
            'is_email_verified': user.is_email_verified
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ================================================================
# File Management Views
# ================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_file(request):
    """File upload for ops users only"""
    if request.user.user_type != 'ops':
        return Response({'error': 'Only operation users can upload files'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = FileUploadSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        uploaded_file = serializer.save()
        
        return Response({
            'message': 'File uploaded successfully',
            'file_id': uploaded_file.id,
            'filename': uploaded_file.original_filename,
            'file_type': uploaded_file.file_type,
            'size': uploaded_file.file_size
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_files(request):
    """List all uploaded files for client users"""
    if request.user.user_type != 'client':
        return Response({'error': 'Only client users can list files'}, status=status.HTTP_403_FORBIDDEN)
    
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    serializer = UploadedFileSerializer(files, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_download_url(request, file_id):
    """Generate secure download URL for client users"""
    if request.user.user_type != 'client':
        return Response({'error': 'Only client users can download files'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        file_obj = UploadedFile.objects.get(id=file_id)
    except UploadedFile.DoesNotExist:
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Generate secure download URL
    token = uuid.uuid4()
    encrypted_data = encrypt_url(f"{file_id}_{request.user.id}_{token}")
    
    # Create secure download record
    secure_url = SecureDownloadURL.objects.create(
        file=file_obj,
        user=request.user,
        encrypted_url=encrypted_data,
        token=token
    )
    
    download_url = f"http://localhost:8000/api/download/{encrypted_data}/"
    
    return Response({
        'download_url': download_url,
        'expires_at': secure_url.expires_at,
        'filename': file_obj.original_filename
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def download_file(request, encrypted_url):
    """Download file using encrypted URL"""
    decrypted_data = decrypt_url(encrypted_url)
    
    if not decrypted_data:
        return Response({'error': 'Invalid download URL'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        parts = decrypted_data.split('_')
        file_id = int(parts[0])
        user_id = int(parts[1])
        token = parts[2]
        
        # Verify secure download record
        secure_url = SecureDownloadURL.objects.get(
            file_id=file_id,
            user_id=user_id,
            token=token,
            is_used=False
        )
        
        if secure_url.is_expired():
            return Response({'error': 'Download URL has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark as used (optional - remove if multiple downloads allowed)
        secure_url.is_used = True
        secure_url.save()
        
        # Serve file
        file_obj = secure_url.file
        
        try:
            with open(file_obj.file.path, 'rb') as f:
                file_data = f.read()
                
            response = HttpResponse(
                file_data,
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{file_obj.original_filename}"'
            return response
            
        except FileNotFoundError:
            return Response({'error': 'File not found on server'}, status=status.HTTP_404_NOT_FOUND)
    
    except (ValueError, IndexError, SecureDownloadURL.DoesNotExist):
        return Response({'error': 'Invalid or expired download URL'}, status=status.HTTP_400_BAD_REQUEST)

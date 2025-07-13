from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UploadedFile, EmailVerification
import magic

# from file_sharing.utils import encrypt_url
try:
    from file_sharing.utils import encrypt_url
except ImportError:
    # Fallback: define a dummy encrypt_url or import from the correct location
    def encrypt_url(value):
        return value  # TODO: Replace with actual implementation or correct import path
import magic

class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'user_type']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        if data['user_type'] not in ['ops', 'client']:
            raise serializers.ValidationError("Invalid user type")
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Generate encrypted signup URL for client users
        if user.user_type == 'client':
            encrypted_url = encrypt_url(f"signup_success_{user.id}")
            user.encrypted_signup_url = encrypted_url
            user.save()
        
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled")
                if user.user_type == 'client' and not user.is_email_verified:
                    raise serializers.ValidationError("Please verify your email first")
                data['user'] = user
            else:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must provide email and password")
        
        return data

class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    
    class Meta:
        model = UploadedFile
        fields = ['file']
    
    def validate_file(self, value):
        # Check file extension
        allowed_extensions = ['pptx', 'docx', 'xlsx']
        file_extension = value.name.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"Only {', '.join(allowed_extensions)} files are allowed"
            )
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        return value
    
    def create(self, validated_data):
        file = validated_data['file']
        
        uploaded_file = UploadedFile.objects.create(
            uploaded_by=self.context['request'].user,
            file=file,
            original_filename=file.name,
            file_size=file.size,
            file_type=file.name.split('.')[-1].lower()
        )
        
        return uploaded_file

class UploadedFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = UploadedFile
        fields = ['id', 'original_filename', 'file_size', 'file_type', 'uploaded_at', 'uploaded_by']

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UploadedFile, EmailVerification, SecureDownloadURL

class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'user_type', 'is_email_verified', 'is_active']
    list_filter = ['user_type', 'is_email_verified', 'is_active']
    search_fields = ['email', 'username']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'is_email_verified', 'encrypted_signup_url')
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(UploadedFile)
admin.site.register(EmailVerification)
admin.site.register(SecureDownloadURL)







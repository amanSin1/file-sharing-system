from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    # Authentication endpoints
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify-email'),
    
    # File management endpoints
    path('upload/', views.upload_file, name='upload-file'),
    path('files/', views.list_files, name='list-files'),
    path('files/<int:file_id>/download-url/', views.get_download_url, name='get-download-url'),
    path('download/<str:encrypted_url>/', views.download_file, name='download-file'),
]
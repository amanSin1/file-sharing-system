

import requests
import json
import os
import time
from io import BytesIO

BASE_URL = "http://localhost:8000/api"

class FileShareAPITester:
    def __init__(self):
        self.ops_token = None
        self.client_token = None
        self.uploaded_file_id = None
        
    def create_test_file(self, filename="test.docx"):
        """Create a test file for upload"""
        test_content = b"This is a test document content for file sharing API testing."
        with open(filename, 'wb') as f:
            f.write(test_content)
        return filename
    
    def test_ops_login(self):
        """Test operation user login"""
        print("\n" + "="*50)
        print("🔐 TESTING OPS USER LOGIN")
        print("="*50)
        
        data = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/login/", json=data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.ops_token = result["access_token"]
                print(f"✅ SUCCESS!")
                print(f"User Type: {result['user_type']}")
                print(f"Email: {result['email']}")
                print(f"Token: {self.ops_token[:50]}...")
                return True
            else:
                print(f"❌ FAILED: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def test_file_upload(self):
        """Test file upload by ops user"""
        print("\n" + "="*50)
        print("📁 TESTING FILE UPLOAD")
        print("="*50)
        
        if not self.ops_token:
            print("❌ No ops token available. Login first.")
            return False
        
        # Create test file
        filename = self.create_test_file()
        
        try:
            headers = {"Authorization": f"Bearer {self.ops_token}"}
            
            with open(filename, 'rb') as f:
                files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                response = requests.post(f"{BASE_URL}/upload/", headers=headers, files=files)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                self.uploaded_file_id = result["file_id"]
                print(f"✅ SUCCESS!")
                print(f"File ID: {result['file_id']}")
                print(f"Filename: {result['filename']}")
                print(f"File Type: {result['file_type']}")
                print(f"Size: {result['size']} bytes")
                
                # Clean up test file
                os.remove(filename)
                return True
            else:
                print(f"❌ FAILED: {response.text}")
                os.remove(filename)
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            if os.path.exists(filename):
                os.remove(filename)
            return False
    
    def test_client_signup(self):
        """Test client user signup"""
        print("\n" + "="*50)
        print("👤 TESTING CLIENT SIGNUP")
        print("="*50)
        
        data = {
            "username": "testclient",
            "email": "client@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "user_type": "client"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/signup/", json=data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ SUCCESS!")
                print(f"User ID: {result['user_id']}")
                print(f"Email: {result['email']}")
                print(f"Encrypted URL: {result.get('encrypted_url', 'Not provided')[:50]}...")
                return True
            else:
                print(f"❌ FAILED: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def test_client_login(self):
        """Test client user login"""
        print("\n" + "="*50)
        print("🔐 TESTING CLIENT LOGIN")
        print("="*50)
        
        data = {
            "email": "client@example.com",
            "password": "password123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/login/", json=data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.client_token = result["access_token"]
                print(f"✅ SUCCESS!")
                print(f"User Type: {result['user_type']}")
                print(f"Email: {result['email']}")
                print(f"Email Verified: {result.get('is_email_verified', False)}")
                print(f"Token: {self.client_token[:50]}...")
                return True
            else:
                print(f"❌ FAILED: {response.text}")
                print("💡 HINT: You might need to verify the email first!")
                print("   Check your Django console for verification link.")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def test_list_files(self):
        """Test listing files by client user"""
        print("\n" + "="*50)
        print("📋 TESTING LIST FILES")
        print("="*50)
        
        if not self.client_token:
            print("❌ No client token available. Login first.")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = requests.get(f"{BASE_URL}/files/", headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS!")
                print(f"Files found: {len(result)}")
                
                for i, file_info in enumerate(result):
                    print(f"\nFile {i+1}:")
                    print(f"  ID: {file_info['id']}")
                    print(f"  Name: {file_info['original_filename']}")
                    print(f"  Type: {file_info['file_type']}")
                    print(f"  Size: {file_info['file_size']} bytes")
                    print(f"  Uploaded by: {file_info['uploaded_by']}")
                    print(f"  Upload time: {file_info['uploaded_at']}")
                
                return True
            else:
                print(f"❌ FAILED: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def test_get_download_url(self):
        """Test getting secure download URL"""
        print("\n" + "="*50)
        print("🔗 TESTING GET DOWNLOAD URL")
        print("="*50)
        
        if not self.client_token:
            print("❌ No client token available. Login first.")
            return False, None
        
        if not self.uploaded_file_id:
            print("❌ No uploaded file ID available. Upload a file first.")
            return False, None
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = requests.get(f"{BASE_URL}/files/{self.uploaded_file_id}/download-url/", headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS!")
                print(f"Download URL: {result['download_url']}")
                print(f"Expires at: {result['expires_at']}")
                print(f"Filename: {result['filename']}")
                return True, result['download_url']
            else:
                print(f"❌ FAILED: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False, None
    
    def test_download_file(self, download_url):
        """Test downloading file using secure URL"""
        print("\n" + "="*50)
        print("⬇️  TESTING FILE DOWNLOAD")
        print("="*50)
        
        if not download_url:
            print("❌ No download URL provided.")
            return False
        
        try:
            response = requests.get(download_url)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS!")
                print(f"File size: {len(response.content)} bytes")
                print(f"Content type: {response.headers.get('content-type', 'Unknown')}")
                
                # Save downloaded file
                with open('downloaded_file.docx', 'wb') as f:
                    f.write(response.content)
                print(f"File saved as: downloaded_file.docx")
                return True
            else:
                print(f"❌ FAILED: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def test_security_violations(self):
        """Test security violations"""
        print("\n" + "="*50)
        print("🔒 TESTING SECURITY VIOLATIONS")
        print("="*50)
        
        # Test 1: Client trying to upload
        print("\n1. Testing: Client user trying to upload file...")
        if self.client_token:
            filename = self.create_test_file("security_test.docx")
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            with open(filename, 'rb') as f:
                files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                response = requests.post(f"{BASE_URL}/upload/", headers=headers, files=files)
            
            if response.status_code == 403:
                print("✅ SECURITY TEST PASSED: Client cannot upload files")
            else:
                print(f"❌ SECURITY ISSUE: Client was able to upload! Status: {response.status_code}")
            
            os.remove(filename)
        
        # Test 2: Ops trying to list files
        print("\n2. Testing: Ops user trying to list files...")
        if self.ops_token:
            headers = {"Authorization": f"Bearer {self.ops_token}"}
            response = requests.get(f"{BASE_URL}/files/", headers=headers)
            
            if response.status_code == 403:
                print("✅ SECURITY TEST PASSED: Ops user cannot list files")
            else:
                print(f"❌ SECURITY ISSUE: Ops user was able to list files! Status: {response.status_code}")
        
        # Test 3: Invalid file type
        print("\n3. Testing: Invalid file type upload...")
        if self.ops_token:
            # Create a .txt file
            with open("invalid.txt", 'w') as f:
                f.write("This is not an allowed file type")
            
            headers = {"Authorization": f"Bearer {self.ops_token}"}
            with open("invalid.txt", 'rb') as f:
                files = {'file': ('invalid.txt', f, 'text/plain')}
                response = requests.post(f"{BASE_URL}/upload/", headers=headers, files=files)
            
            if response.status_code == 400:
                print("✅ SECURITY TEST PASSED: Invalid file type rejected")
            else:
                print(f"❌ SECURITY ISSUE: Invalid file type was accepted! Status: {response.status_code}")
            
            os.remove("invalid.txt")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 STARTING COMPLETE API TESTING SUITE")
        print("="*60)
        
        # Test Ops User Flow
        print("\n📊 TESTING OPS USER FLOW:")
        ops_login_success = self.test_ops_login()
        if ops_login_success:
            self.test_file_upload()
        
        # Test Client User Flow
        print("\n📊 TESTING CLIENT USER FLOW:")
        client_signup_success = self.test_client_signup()
        if client_signup_success:
            client_login_success = self.test_client_login()
            if client_login_success:
                self.test_list_files()
                download_url_success, download_url = self.test_get_download_url()
                if download_url_success:
                    self.test_download_file(download_url)
        
        # Test Security
        print("\n📊 TESTING SECURITY:")
        self.test_security_violations()
        
        print("\n" + "="*60)
        print("🎉 TESTING COMPLETE!")
        print("="*60)
        
        # Summary
        print("\n📋 SUMMARY:")
        print("✅ If you see green checkmarks, the tests passed!")
        print("❌ If you see red X marks, check the error messages.")
        print("💡 If client login fails, check Django console for email verification link.")
        print("\n📁 Files created during testing:")
        print("- downloaded_file.docx (if download test passed)")
        print("\n🔗 Next steps:")
        print("1. Fix any failing tests")
        print("2. Try the API endpoints manually with Postman/curl")
        print("3. Check Django admin panel for user management")

if __name__ == "__main__":
    tester = FileShareAPITester()
    tester.run_all_tests()
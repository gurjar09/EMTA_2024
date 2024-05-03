from .views import *
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', VendorSignup, name='VendorSignup'),  
    path('VendorDashboard/', VendorDashboard, name='VendorDashboard'),
    path('VendorLogin/', VendorLogin, name='VendorLogin'),
    path('VendorSignup/', VendorSignup, name='VendorSignup'),
    path('candidateform/', candidateform, name='candidateform'),
    path('candidate/details/<int:candidate_id>/', CandidateDetails, name='candidate_details'),
    path('VendorLogout/', VendorLogout, name='VendorLogout'),
    path('candidate_success/<int:candidate_id>/', CandidateSuccess, name='candidate_success'),
    path('Profile/', Profile, name='profile_details'),
    path('EstablishmentDetails/', EstablishmentDetails, name='establishment_details'),
    path('Bank_Details/', Bank_Details, name='bank_details'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password/<str:username>/', reset_password, name='reset_password'),
    path('adminDashboard/', adminDashBoard, name='admin_dashboard'),
    path('vendor/<str:vendor_code>/candidates/', vendor_candidates, name='vendor_candidates'),
    path('candidateDashboard/', candidateDashboard, name='candidate_dashboard'),
    path('EmployeeDashboard/', EmployeeDashboard, name='EmployeeDashboard'),
    path('Employeecandidate/', Employeecandidate, name='Employeecandidate'),
    path('EmployeeVendorCandidate/<str:vendor_code>/', Employee_vendorecandidate, name='Employee_vendorecandidate'),
    path('EmployeeSignup/', employee_signup, name='EmployeeSignup'),
    path('EmployeeLogin/', employee_login, name='EmployeeLogin'),
    path('employee_logout/', employee_logout, name='employee_logout'),
    path('EmployeeDetails/', EmployeeDetails, name='employee_details'),
    path('AdminVendorDetails',AdminVendorDetails , name= 'Admin_Vendor_details'),
    path('vendor/<int:vendor_id>/details/', AdminVendorDetails, name='admin_vendor_details'),
    path('admin/vendor/<int:vendor_id>/details/', AdminVendorDetails, name='admin_vendor_details'),

    path('admin/', admin.site.urls),
]

# For serving media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
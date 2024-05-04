from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model



class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15)
    shop_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    refer_code = models.CharField(max_length=10, unique=True)
    date_of_birth = models.TextField(max_length=10)
    profile_image = models.FileField(upload_to='profile/')
    # vendorCommission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    CommissionReceived = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    profileVerification = [
        ('Under Process', 'Under Process'),
        ('Verified', 'Verified'),
        ('Rejected(Upload Details Again)', 'Rejected(Upload Details Again)'),
    ]
    profileVerification = models.CharField(max_length=50, choices=profileVerification,default='Under Process')    
    total_commission_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    
    def get_or_create_profile_document(self):
        profile_document, created = ProfileDocument.objects.get_or_create(vendor=self)
        return profile_document
    def get_or_create_BussinessDetails(self):
        Bussiness_Details, created = BussinessDetails.objects.get_or_create(vendor=self)
        return Bussiness_Details
    def get_or_create_BankDetails(self):
        bank_details, created = Bank.objects.get_or_create(vendor=self)
        return bank_details
    

class CustomUser(User):
    def save(self, *args, **kwargs):
        if not self.pk:  # New instance
            # Set username to the generated refer code
            self.username = self.vendor.refer_code
        super().save(*args, **kwargs)

# Override the default User model with the custom one
User = CustomUser
    
   
class Candidate(models.Model):
    refer_code = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    qualification = models.CharField(max_length = 100)
    mobile_number = models.BigIntegerField()
    email = models.EmailField()
    status = [
        ('Pending', 'Pending'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
        ('Hold', 'Hold'),
    ]
    status = models.CharField(max_length=10, choices=status , default='Pending')
    Contact = [
        ('No', 'No'),
        ('Yes', 'Yes'),
    ]
    Contact = models.CharField(max_length=10, choices=Contact , default='No')
    resume = models.FileField(upload_to='candidate/resume/')
    sector = models.CharField(max_length=50)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=50)
    totalCommission = models.CharField(max_length=10)
    Contact_by = models.CharField(max_length=50,default='None')
    
    
class ProfileDocument(models.Model) :
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    adhar_card = models.CharField(max_length=15)
    pan_card = models.CharField(max_length=15)
    adhar_image = models.FileField(upload_to='adhar/')
    pan_image = models.FileField(upload_to='pan/')

class BussinessDetails(models.Model) :
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    Gumasta = models.FileField(upload_to='Gumasata/')
    gst_number = models.CharField(max_length=20)
    gst_image = models.FileField(upload_to='GST/') 
    Bpan_number = models.CharField(max_length=15)
    Bpan_image = models.FileField(upload_to='Bussiness pan card/')
    MSME_number = models.CharField(max_length=15)
    MSME_image = models.FileField(upload_to='MSME/')
    Contact_number = models.CharField(max_length=12)
    Bphoto_outer = models.FileField(upload_to='Bussiness photo/outer')
    Bphoto_inside = models.FileField(upload_to='Bussiness photo/inside')
    Gumasta_number = models.CharField(max_length=15)
    
class Bank(models.Model) :
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    bank_document = models.FileField(upload_to='Bank/')
    account_type = [
        ('Saving', 'Saving'),
        ('Current', 'Current'),
    ]
    account_type = models.CharField(max_length=10, choices=account_type)
    preffered_payout_date = [
        ('05', '05'),
        ('15', '15'),
        ('25', '25'),
    ]
    preffered_payout_date = models.CharField(max_length=10, choices=preffered_payout_date)
    account_holder_name = models.CharField(max_length=50)
    account_number1 = models.CharField(max_length=20)
    ifs_code = models.CharField(max_length=20)
    micr_code = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=20)

class ReferredVendor(models.Model):
    referring_vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='referred_vendors')
    referred_vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='referring_vendor')

CustomUser = get_user_model()

class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee')
    mobile_number = models.CharField(max_length=15)
    employee_id = models.CharField(max_length=20)
    def __str__(self):
        return self.user.username
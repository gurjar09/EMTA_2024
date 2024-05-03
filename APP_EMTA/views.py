from django.contrib.auth import authenticate, login ,logout
from django.shortcuts import get_object_or_404, render,redirect                   
from .urls import *
from .models import *
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, ExpressionWrapper, IntegerField
from django.core.exceptions import ObjectDoesNotExist


def VendorDashboard(request):
    if request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
            referral_link = request.build_absolute_uri('/candidateform/?ref={}'.format(vendor.refer_code))
            candidates = Candidate.objects.filter(refer_code=vendor.refer_code)
            num_candidates = candidates.count()
            
            # Calculate total commission for the vendor
            total_commission = candidates.aggregate(total_commission=Sum('commission'))['total_commission']
            
            if request.method == 'POST' and request.FILES.get('profile_picture'):
                profile_picture = request.FILES['profile_picture']
                vendor.profile_image = profile_picture
                vendor.save()
            
            context = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'shop_name': vendor.shop_name,
                # 'vendorCommission': vendor.vendorCommission,
                'candidates': candidates,
                'num_candidates': num_candidates,
                'total_commission': total_commission,
                'profile_picture': vendor.profile_image.url if vendor.profile_image else None,
                'referral_link': referral_link,
                
            }
            return render(request, 'VendorDashboard.html', context)
        except Vendor.DoesNotExist:
            return render(request, 'VendorLogin.html', {'error': 'Vendor details not found'})
    else:
        return render(request, 'username.html', {'error': 'User not authenticated'})

def candidateform(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        qualification = request.POST.get('qualification')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        resume = request.FILES.get('resume')
        sector = request.POST.get('sector')
        location = request.POST.get('location')
        refer_code = request.POST.get('refer_code', '')
        totalCommission = request.POST.get('totalCommission')
        commission = request.POST.get('commission') 
        Contact = request.POST.get('Contact')
        status = request.POST.get('status')
        Contact_by = request.POST.get('Contact_by')


        # Create Candidate object
        candidate = Candidate.objects.create(
            first_name=first_name,
            last_name=last_name,
            qualification=qualification,
            mobile_number=mobile_number,
            email=email,
            resume=resume,
            sector=sector,
            location=location,
            refer_code=refer_code,
            
        )

        # Redirect to success page after form submission
        return redirect(CandidateSuccess, candidate_id=candidate.id)
    
    else:
        refer_code = request.GET.get('ref', '')  # Get referral code from query parameter
        initial_data = {'refer_code': refer_code}  # Pass referral code as initial data to the form
        return render(request, 'candidateform.html', {'initial_data': initial_data})

def CandidateDetails(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    initial_data = {
        'commission': candidate.commission,
        'totalCommission': candidate.totalCommission,
        'Contact': candidate.Contact,
        'status': candidate.status,
        'Contact_by' : candidate.Contact_by,
        'resume': candidate.resume.url if candidate.resume else None
    }
    if request.method == 'POST':
        candidate.commission = request.POST.get('commission')
        candidate.totalCommission = request.POST.get('totalCommission')
        candidate.Contact = request.POST.get('Contact')
        candidate.status = request.POST.get('status')
        candidate.Contact_by = request.POST.get('Contact_by')
        candidate.save()
        return redirect('CandidateDetails', candidate_id=candidate_id)
    return render(request, 'CandidateDetails.html', {'candidate': candidate, 'initial_data': initial_data})

def VendorLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(VendorDashboard)  
        else:
            error_message = "Invalid username or password. Please try again."
            return render(request, 'VendorLogin.html', {'error_message': error_message})
    else:
        return render(request, 'VendorLogin.html')
    
def VendorSignup(request):
    if request.method == 'POST':
        # Extract user data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        refer_code = username

        if not username:
            messages.error(request, 'Username must be set')
            return render(request, 'VendorSignup.html')

        # Validate passwords
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'VendorSignup.html')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken')
            return render(request, 'VendorSignup.html')

        # Create the user object
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Create the vendor object without setting vendorCommission
        vendor = Vendor.objects.create(user=user, mobile_number=mobile_number, refer_code=refer_code)
        
        # Redirect to the login page
        return redirect(VendorLogin)
    
    # Render the signup page for GET requests
    return render(request, 'VendorSignup.html')
def VendorLogout(request):
    logout(request)
    return redirect(VendorLogin)

def CandidateSuccess(request,candidate_id) :
    return render(request , 'CandidateSuccess.html')


@login_required
def Profile(request):
    if request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
            profile_document, created = ProfileDocument.objects.get_or_create(vendor=vendor)

            if request.method == 'POST':
                # Handle profile update
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                shop_name = request.POST.get('shop_name')
                mobile_number = request.POST.get('mobile_number')
                address = request.POST.get('address')
                date_of_birth = request.POST.get('date_of_birth')

                # Update User model fields
                user = request.user
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                # Update Vendor model fields
                vendor.shop_name = shop_name
                vendor.mobile_number = mobile_number
                vendor.address = address
                vendor.date_of_birth = date_of_birth
                vendor.save()

                # Handle profile document update
                adhar_card = request.POST.get('adhar_card')
                pan_card = request.POST.get('pan_card')
                adhar_image = request.FILES.get('adhar_image')
                pan_image = request.FILES.get('pan_image')

                profile_document.adhar_card = adhar_card
                profile_document.pan_card = pan_card
                if adhar_image:
                    profile_document.adhar_image = adhar_image
                if pan_image:
                    profile_document.pan_image = pan_image
                profile_document.save()

                return redirect(Profile)

            # Get verification status
            profileVerification = vendor.profileVerification

            # Get URLs of previous images
            adhar_image_url = profile_document.adhar_image.url if profile_document.adhar_image else None
            pan_image_url = profile_document.pan_image.url if profile_document.pan_image else None

            context = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'shop_name': vendor.shop_name,
                'mobile_number': vendor.mobile_number,
                'address': vendor.address,
                'date_of_birth': vendor.date_of_birth,
                'adhar_card': profile_document.adhar_card,
                'pan_card': profile_document.pan_card,
                'adhar_image_url': adhar_image_url,
                'pan_image_url': pan_image_url,
                'verification_status': profileVerification,  # Add verification status to context
            }
            return render(request, 'Profile.html', context)

        except Vendor.DoesNotExist:
            return render(request, 'usernotfound.html', {'error': 'Vendor details not found'})
        except ProfileDocument.DoesNotExist:
            return render(request, 'Profile.html', {'error': 'Profile document not found'})

    else:
        return render(request, 'username.html', {'error': 'User not authenticated'})



    
# def uploadProfilePhoto(request):
#     if request.method == 'POST':
#         profile_image = request.FILES.get('profile_image')
#         vendor = Vendor.objects.get(user=request.user)
#         vendor.profile_image = profile_image
#         vendor.save()
#         return redirect(Profile)
#     else:
#         return render(request, 'uploadProfilePhoto.html')

@login_required
def EstablishmentDetails(request):
    if request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
            bussiness_profile, _ = BussinessDetails.objects.get_or_create(vendor=vendor)
            
            context = {
                'first_name': request.user.first_name.capitalize(),
                'last_name': request.user.last_name.capitalize(),
                'shop_name': vendor.shop_name.capitalize(),
                'mobile_number': vendor.mobile_number,
                'address': vendor.address,
                'date_of_birth': vendor.date_of_birth,
                'gst_number': bussiness_profile.gst_number,
                'Bpan_number': bussiness_profile.Bpan_number,
                'MSME_number': bussiness_profile.MSME_number,
                'Contact_number': bussiness_profile.Contact_number,
                'Gumasta_number' : bussiness_profile.Gumasta_number
            }
            if request.method == 'POST':
                # Handle form submission
                # Retrieve form data
                gst_number = request.POST.get('gst_number')
                Bpan_number = request.POST.get('Bpan_number')
                MSME_number = request.POST.get('MSME_number')
                Contact_number = request.POST.get('Contact_number')
                Gumasta_number = request.POST.get('Gumasta_number')
                Bpan_image = request.FILES.get('Bpan_image')
                gst_image = request.FILES.get('gst_image')
                Gumasta = request.FILES.get('Gumasta')
                MSME_image = request.FILES.get('MSME_image')
                Bphoto_outer = request.FILES.get('Bphoto_outer')
                Bphoto_inside = request.FILES.get('Bphoto_inside')

                # Update fields with form data
                bussiness_profile.gst_number = gst_number
                bussiness_profile.Bpan_number = Bpan_number
                bussiness_profile.MSME_number = MSME_number
                bussiness_profile.Contact_number = Contact_number
                bussiness_profile.Gumasta_number = Gumasta_number

                # Handle file uploads
                if Bpan_image:
                    bussiness_profile.Bpan_image = Bpan_image
                if gst_image:
                    bussiness_profile.gst_image = gst_image
                if Gumasta:
                    bussiness_profile.Gumasta = Gumasta
                if MSME_image:
                    bussiness_profile.MSME_image = MSME_image
                if Bphoto_outer:
                    bussiness_profile.Bphoto_outer = Bphoto_outer
                if Bphoto_inside:
                    bussiness_profile.Bphoto_inside = Bphoto_inside

                bussiness_profile.save()

                return redirect(EstablishmentDetails)

            return render(request, 'EstablishmentDetails.html', context)
        except Vendor.DoesNotExist:
            return render(request, 'usernotfound.html', {'error': 'Vendor details not found'})
        except BussinessDetails.DoesNotExist:
            return render(request, 'EstablishmentDetails.html', {'error': 'Business details not found'})
    else:
        return render(request, 'username.html', {'error': 'User not authenticated'})
@login_required
def Bank_Details(request):
    if request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
            bank_details, created = Bank.objects.get_or_create(vendor=vendor)

            if request.method == 'POST':
                bank_document = request.FILES.get('bank_document')
                account_type = request.POST.get('account_type')
                preffered_payout_date = request.POST.get('preffered_payout_date')
                account_holder_name = request.POST.get('account_holder_name')
                account_number1 = request.POST.get('account_number1')
                account_number2 = request.POST.get('account_number2')
                ifs_code = request.POST.get('ifs_code')
                micr_code = request.POST.get('micr_code')
                bank_name = request.POST.get('bank_name')

                if account_number1 != account_number2:
                    return render(request, 'password.html', {'error': 'Account numbers do not match'})

                bank_details.bank_document = bank_document
                bank_details.account_type = account_type
                bank_details.preffered_payout_date = preffered_payout_date
                bank_details.account_holder_name = account_holder_name.capitalize()
                bank_details.account_number1 = account_number1 if account_number1 else None
                bank_details.ifs_code = ifs_code
                bank_details.micr_code = micr_code
                bank_details.bank_name = bank_name
                bank_details.save()

                return redirect(Bank_Details)

            context = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'account_holder_name': bank_details.account_holder_name,
                'account_number1': bank_details.account_number1,
                'ifs_code': bank_details.ifs_code,
                'micr_code': bank_details.micr_code,
                'bank_name': bank_details.bank_name,
                'account_type': bank_details.account_type if bank_details.account_type else '',
                'preffered_payout_date': bank_details.preffered_payout_date if bank_details.preffered_payout_date else [],
                'bank_document_url': bank_details.bank_document.url if bank_details.bank_document else None,
            }
            return render(request, 'VendorBankDetails.html', context)
        
        except Vendor.DoesNotExist:
            return render(request, 'usernotfound.html', {'error': 'Vendor details not found'})
        except Bank.DoesNotExist:
            return render(request, 'VendorBankDetails.html', {'error': 'Bank details not found'})
    else:
        return render(request, 'username.html', {'error': 'User not authenticated'})


# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from django.contrib import messages

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Extract username from the form data
        user = User.objects.filter(username=username).first()
        if user:
            return redirect('reset_password', username=username)
        else:
            messages.error(request, 'User with this username does not exist')
            return redirect('forgot_password')
    else:
        return render(request, 'forgot_password.html')

def reset_password(request, username):
    user = User.objects.filter(username=username).first()
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            user.set_password(password1)
            user.save()
            messages.success(request, 'Password reset successfully.')
            return redirect(VendorLogin)
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'reset_password.html')

# def VendorCommission(request) :
#     vendorCommission = request.POST.get('vendorCommission')
#     vendor = Vendor.objects.get(user=request.user)
#     vendor_commission , created = VendorCommission.objects.get_or_create(vendor = vendor)
#     vendor_commission.save()
#     return render(request,'VendorCommission.html')


def adminDashBoard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            # Check if the request is for deleting a vendor
            vendor_id = request.POST.get('vendor_id')
            if vendor_id:
                # Perform the deletion
                try:
                    vendor = Vendor.objects.get(pk=vendor_id)
                    vendor.delete()
                    messages.success(request, 'Vendor deleted successfully.')
                    # Redirect to avoid form resubmission
                    return redirect('admin_dashboard')
                except Vendor.DoesNotExist:
                    messages.error(request, 'Vendor does not exist.')

        try:
            # Get the name of the superuser
            superuser_name = request.user.username.capitalize()

            # Retrieve vendors and other data
            username_query = request.GET.get('username', '')
            vendors = Vendor.objects.filter(user__username__icontains=username_query)
            
            # Calculate total commission of all candidates
            total_candidate_commission = Candidate.objects.aggregate(total_commission=Sum('commission'))['total_commission']
            
            # Calculate total commission of all vendors
            total_vendor_commission = Vendor.objects.aggregate(total_commission_received=Sum('total_commission_received'))['total_commission_received']
            
            users = User.objects.filter(is_superuser=False)
            user_data = []
            for user in users:
                profile = None  # Initialize profile outside the try block
                try:
                    profile = Vendor.objects.get(user=user)
                    document_id = profile.profiledocument.id  # Assuming ProfileDocument is related to Vendor
                    bussiness_id = profile.bussinessdetails.id  # Assuming BussinessDetails is related to Vendor
                    bank_id = profile.bank.id  # Assuming Bank is related to Vendor
                except ObjectDoesNotExist:
                    pass  # No need to handle here, profile will remain None if not found

                if profile:
                    user_data.append({
                        'user': user,
                        'shop_name': profile.shop_name.capitalize(),
                        'mobile_number': profile.mobile_number,
                        'vendor_commission': profile.total_commission_received,
                        'CommissionReceived': profile.CommissionReceived,
                        'document_id': document_id,
                        'bussiness_id': bussiness_id,
                        'bank_id': bank_id,
                        'vendor_id': profile.id,  # Add vendor ID for deletion
                    })
                

            vendor_count = Vendor.objects.count()
            total_candidates_all = Candidate.objects.all().count()
            current_month = timezone.now().month
            current_year = timezone.now().year
            vendors_this_month = Vendor.objects.filter(user__date_joined__year=current_year, user__date_joined__month=current_month).count()

            # Check if user_data is empty
            if not user_data:
                no_vendors_message = 'No vendors found.'
                return render(request, 'AdminDashBoard.html', {'no_vendors_message': no_vendors_message, 'superuser_name': superuser_name})
            
            return render(request, 'AdminDashBoard.html', {'user_data': user_data, 'vendor_count': vendor_count, 'vendors_this_month': vendors_this_month, 'total_vendor_commission': total_vendor_commission, 'total_candidate_commission': total_candidate_commission , 'total_candidates_all': total_candidates_all, 'username_query': username_query, 'superuser_name': superuser_name})
        except User.DoesNotExist:
            return render(request, 'usernotfound.html', {'error': 'User details not found'})
    else:
        return render(request, 'username.html', {'error': 'User not authenticated or not a superuser'})



def vendor_candidates(request, vendor_code):
    try:
        # Fetch the vendor object using the vendor_code
        vendor = Vendor.objects.get(refer_code=vendor_code)
        candidates = Candidate.objects.filter(refer_code=vendor_code)
        total_candidates = candidates.count()
        
        # Get the name of the superuser
        superuser_name = request.user.username.capitalize()
        

        vendor_name = vendor.user.first_name.capitalize()
        vendor_last_name = vendor.user.last_name.capitalize()

        return render(request, 'VendorsCandidate.html', { 'vendor': vendor, 'candidates': candidates, 'vendor_name': vendor_name, 'vendor_last_name': vendor_last_name, 'total_candidates': total_candidates, 'superuser_name': superuser_name})
    except Vendor.DoesNotExist:
        return render(request, 'vendor_not_found.html', {'error': 'Vendor not found'})

from django.db.models import Q

from django.http import HttpResponseRedirect
from django.urls import reverse

def candidateDashboard(request):
    candidates = Candidate.objects.all()
    total_candidates_all = candidates.count()
    superuser_name = request.user.username.capitalize()
    employee_id = None

    # Get the employee ID of the user if available
    if request.user.is_authenticated:
        try:
            employee_id = request.user.employee.employee_id
        except AttributeError:
            # Handle the case where the employee ID is not available for the user
            pass

    # Handling filter queries
    if request.method == 'GET':
        contact_filter = request.GET.get('contact', '')
        contact_by_filter = request.GET.get('contact_by', '')
        refer_code_filter = request.GET.get('refer_code', '')
        name_filter = request.GET.get('name', '')
        mobile_filter = request.GET.get('mobile', '')
        email_filter = request.GET.get('email', '')
        location_filter = request.GET.get('location', '')
        job_preference_filter = request.GET.get('job_preference', '')
        status_filter = request.GET.get('status', '')

        # Applying filters to the queryset
        if contact_filter:
            candidates = candidates.filter(Contact__icontains=contact_filter)
        if contact_by_filter:
            candidates = candidates.filter(Contact_by__icontains=contact_by_filter)
        if refer_code_filter:
            candidates = candidates.filter(refer_code__icontains=refer_code_filter)
        if name_filter:
            candidates = candidates.filter(Q(first_name__icontains=name_filter) | Q(last_name__icontains=name_filter))
        if mobile_filter:
            candidates = candidates.filter(mobile_number__icontains=mobile_filter)
        if email_filter:
            candidates = candidates.filter(email__icontains=email_filter)
        if location_filter:
            candidates = candidates.filter(location__icontains=location_filter)
        if job_preference_filter:
            candidates = candidates.filter(sector__icontains=job_preference_filter)
        if status_filter:
            candidates = candidates.filter(status__icontains=status_filter)

    # Handling candidate deletion
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        try:
            candidate_to_delete = Candidate.objects.get(pk=candidate_id)
            candidate_to_delete.delete()
            # Redirect to the same page after deletion
            return HttpResponseRedirect(reverse(candidateDashboard))
        except ObjectDoesNotExist:
            # Candidate with the provided ID does not exist
            pass
        except Exception as e:
            # Handle other exceptions if necessary
            pass

    return render(request, 'candidateDashboard.html', {
        'candidates': candidates,
        'total_candidates_all': total_candidates_all,
        'superuser_name': superuser_name,
        'employee_id': employee_id,
    })



@login_required
def EmployeeDashboard(request):
    try:
        # Get the name of the user
        user_name = request.user.username.capitalize()

        # Retrieve vendors and other data
        username_query = request.GET.get('username', '')
        vendors = Vendor.objects.filter(user__username__icontains=username_query)
        
        # Calculate total commission of all candidates
        total_candidate_commission = Candidate.objects.aggregate(total_commission=Sum('commission'))['total_commission']
        username = request.user.username
        
        # Calculate total commission of all vendors
        total_vendor_commission = Vendor.objects.aggregate(total_commission_received=Sum('total_commission_received'))['total_commission_received']
        
        users = User.objects.filter(is_superuser=False)
        user_data = []
        for user in users:
            profile = None  # Initialize profile to None
            try:
                profile = Vendor.objects.get(user=user)
                document_id = profile.profiledocument.id  # Assuming ProfileDocument is related to Vendor
                bussiness_id = profile.bussinessdetails.id  # Assuming BussinessDetails is related to Vendor
                bank_id = profile.bank.id  # Assuming Bank is related to Vendor
            except ObjectDoesNotExist:
                pass  # Do nothing if profile does not exist

            if profile:
                user_data.append({
                    
                    'user': user,
                    'shop_name': profile.shop_name.capitalize(),
                    'mobile_number': profile.mobile_number,
                    'vendor_commission': profile.total_commission_received,
                    'CommissionReceived': profile.CommissionReceived,
                    'document_id': document_id,
                    'bussiness_id': bussiness_id,
                    'bank_id': bank_id,
                })

        vendor_count = Vendor.objects.count()
        total_candidates_all = Candidate.objects.all().count()
        current_month = timezone.now().month
        current_year = timezone.now().year
        vendors_this_month = Vendor.objects.filter(user__date_joined__year=current_year, user__date_joined__month=current_month).count()

        return render(request, 'EmployeeAdminDashboard.html', {'username': username,'user_data': user_data, 'vendor_count': vendor_count, 'vendors_this_month': vendors_this_month, 'total_vendor_commission': total_vendor_commission, 'total_candidate_commission': total_candidate_commission , 'total_candidates_all': total_candidates_all, 'username_query': username_query, 'user_name': user_name})
    except User.DoesNotExist:
        return render(request, 'usernotfound.html', {'error': 'User details not found'})
    
def Employeecandidate(request):
    candidates = Candidate.objects.all()
    total_candidates_all = candidates.count()
    superuser_name = request.user.username.capitalize()

    # Handling search query
    search_query = request.GET.get('search_query')
    if search_query:
        candidates = candidates.filter(
            Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query) | 
            Q(mobile_number__icontains=search_query) | Q(email__icontains=search_query) | 
            Q(location__icontains=search_query) | Q(sector__icontains=search_query) | 
            Q(status__icontains=search_query)
        )

    return render(request, 'Employeecandidate.html', {'candidates': candidates, 'total_candidates_all': total_candidates_all, 'superuser_name': superuser_name})


def Employee_vendorecandidate(request, vendor_code):
    try:
        # Fetch the vendor object using the vendor_code
        vendor = Vendor.objects.get(refer_code=vendor_code)
        candidates = Candidate.objects.filter(refer_code=vendor_code)
        total_candidates = candidates.count()
        
        # Get the name of the superuser
        superuser_name = request.user.username.capitalize()
        

        vendor_name = vendor.user.first_name.capitalize()
        vendor_last_name = vendor.user.last_name.capitalize()

        return render(request, 'EmployeVendorCandidate.html', { 'vendor': vendor, 'candidates': candidates, 'vendor_name': vendor_name, 'vendor_last_name': vendor_last_name, 'total_candidates': total_candidates, 'superuser_name': superuser_name})
    except Vendor.DoesNotExist:
        return render(request, 'vendor_not_found.html', {'error': 'Vendor not found'})
    
def employee_login(request):
    if request.method == 'POST':
        employee_id = request.POST['employee_id']  # Assuming employee ID is entered in the login form
        password = request.POST['password']
        
        # Authenticate user using employee ID
        user = authenticate(request, username=employee_id, password=password)
        
        if user is not None:
            login(request, user)
            return redirect(EmployeeDashboard)  # Redirect to employee dashboard after successful login
        else:
            error_message = "Invalid employee ID or password. Please try again."
            return render(request, 'employee_login.html', {'error_message': error_message})
    else:
        return render(request, 'employee_login.html')

def employee_signup(request):
    if request.method == 'POST':
        # Extract user data from the form
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        employee_id = request.POST.get('employee_id')

        if not email or not mobile_number or not password1 or not password2 or not employee_id:
            messages.error(request, 'All fields are required')
            return render(request, 'employee_signup.html')

        # Validate passwords
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'employee_signup.html')

        # Check if employee ID already exists
        if User.objects.filter(username=employee_id).exists():
            messages.error(request, 'Employee ID is already taken')
            return render(request, 'employee_signup.html')

        # Create the user object
        user = User.objects.create_user(username=employee_id, email=email, password=password1)
        user.save()

        # Create the employee object
        employee = Employee.objects.create(user=user, mobile_number=mobile_number, employee_id=employee_id)

        # Log in the user after signup
        login(request, user)

        # Redirect to the dashboard or any other page
        return redirect(employee_login)
    
    # Render the signup page for GET requests
    return render(request, 'employee_signup.html')
def employee_logout(request):
    logout(request)
    return redirect(employee_login)
@login_required
def EmployeeDetails(request):
    try:
        # Fetch all employee data
        employees = Employee.objects.all()
        
        context = {
            'employees': employees,
        }

        return render(request, 'EmployeeDetails.html', context)
    except Employee.DoesNotExist:
        return render(request, 'usernotfound.html', {'error': 'Employee details not found'})
    

# views.py
def AdminVendorDetails(request, vendor_id):
    # Retrieve the vendor object by its ID or return a 404 error if not found
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    # Retrieve bank details of the vendor
    bank_details = Bank.objects.filter(vendor=vendor).first()
    
    # Retrieve profile document of the vendor
    profile_document = ProfileDocument.objects.filter(vendor=vendor).first()
    
    # Retrieve business details of the vendor
    business_details = BussinessDetails.objects.filter(vendor=vendor).first()
    
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    # Retrieve bank details of the vendor
    bank_details = Bank.objects.filter(vendor=vendor).first()
    
    # Retrieve profile document of the vendor
    profile_document = ProfileDocument.objects.filter(vendor=vendor).first()
    
    # Retrieve business details of the vendor
    business_details = BussinessDetails.objects.filter(vendor=vendor).first()
    
    # Get URLs of previous images
    adhar_image_url = profile_document.adhar_image.url if profile_document.adhar_image else None
    pan_image_url = profile_document.pan_image.url if profile_document.pan_image else None
    bpan_image_url = business_details.Bpan_image.url if business_details.Bpan_image else None
    gst_image_url = business_details.gst_image.url if business_details.gst_image else None
    gumasta_image_url = business_details.Gumasta.url if business_details.Gumasta else None
    msme_image_url = business_details.MSME_image.url if business_details.MSME_image else None
    bphoto_outer_image_url = business_details.Bphoto_outer.url if business_details.Bphoto_outer else None
    bphoto_inside_image_url = business_details.Bphoto_inside.url if business_details.Bphoto_inside else None
    bank_document_url = bank_details.bank_document.url if bank_details.bank_document else None
    
    if request.method == 'POST':
        # Handle form submission and update vendor details based on the submitted form data
        vendor.user.first_name = request.POST.get('first_name', '')
        vendor.user.last_name = request.POST.get('last_name', '')
        vendor.mobile_number = request.POST.get('mobile_number', '')
        vendor.user.email = request.POST.get('email', '')
        vendor.date_of_birth = request.POST.get('date_of_birth', '')
        vendor.shop_name = request.POST.get('shop_name', '')
        vendor.address = request.POST.get('address', '')
        vendor.profile_verification = request.POST.get('profile_verification', '')
        vendor.save()
        
        # Update bank details
        bank_details.account_holder_name = request.POST.get('account_holder_name', '')
        bank_details.account_number = request.POST.get('account_number', '')
        bank_details.ifs_code = request.POST.get('ifs_code', '')
        bank_details.micr_code = request.POST.get('micr_code', '')
        bank_details.bank_name = request.POST.get('bank_name', '')
        bank_details.save()
        
        # Update profile document details
        profile_document.adhar_card = request.POST.get('adhar_card', '')
        profile_document.pan_card = request.POST.get('pan_card', '')
        profile_document.save()
        
        # Update business details
        business_details.gst_number = request.POST.get('gst_number', '')
        business_details.msme_number = request.POST.get('msme_number', '')
        business_details.gumasta_number = request.POST.get('gumasta_number', '')
        business_details.save()
        
        # Redirect to a success page or any other appropriate page
        return redirect(AdminVendorDetails)  # Replace 'success_page' with the name of your success page URL pattern
    
    # Pass the vendor details and image URLs to the template for rendering the form
    return render(request, 'AdminVendorDetails.html', {
        'vendor': vendor,
        'bank_details': bank_details,
        'profile_document': profile_document,
        'business_details': business_details,
        'adhar_image_url': adhar_image_url,
        'pan_image_url': pan_image_url,
        'bpan_image_url': bpan_image_url,
        'gst_image_url': gst_image_url,
        'gumasta_image_url': gumasta_image_url,
        'msme_image_url': msme_image_url,
        'bphoto_outer_image_url': bphoto_outer_image_url,
        'bphoto_inside_image_url': bphoto_inside_image_url,
        'bank_document_url' : bank_document_url
    })
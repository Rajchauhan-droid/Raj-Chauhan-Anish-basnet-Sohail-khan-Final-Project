# Importing necessary modules and classes from Django
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderProduct

# Importing modules for email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Importing requests for handling HTTP requests
import requests

# Importing necessary modules from other app components
from carts.utils import _cart_id
from carts.models import Cart, CartItem

# Defining views for account functionalities

# View for customer registration
def register(request):
    if request.method == 'POST':
        # If the form is submitted
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # If form data is valid, create a new user
            # Extracting form data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]  # Creating username from email
            # Creating user object
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # Sending verification email
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # Redirecting to login page with verification message
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        # If it's a GET request, render registration form
        form = RegistrationForm()
    context = {
        'form': form,
    }

    return render(request, 'accounts/register.html', context)


# View for customer login
def login(request):
    if request.method == 'POST':
        # If the form is submitted
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # If user is authenticated
            # Handling cart items if any
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # Loop through cart items and update quantities if variations match
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                            messages.success(request, 'Item added to cart successfully')
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
            
            # Authenticate user and redirect accordingly
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                # Redirecting to the next page if specified
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect("dashboard")

        else:
            messages.error(request,'invalid login credentials')
            return redirect("login")
    return render(request, 'accounts/login.html')


# View for logging out
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


# View for account activation
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Activate user account
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

from django.core.exceptions import ObjectDoesNotExist

# View for dashboard panel
@login_required(login_url='login')
def dashboard(request):
    user_id = request.user.id

    # Fetching orders for the current user
    orders = Order.objects.filter(user_id=user_id, is_ordered=True).order_by('created_at')
    orders_count = orders.count()

    try:
        # Trying to get user profile information
        userprofile = UserProfile.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        # Handling the case where UserProfile does not exist for the user
        userprofile = None  # You can provide a default value or handle it as needed

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }

    return render(request, 'accounts/dashboard.html', context)


# View for password reset request
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Sending password reset email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


# View for password reset validation
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'Your password reset link has expired')
        return redirect('login')


# View for password reset form
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')


# View for displaying user's orders
@login_required(login_url='login')
def my_orders(request):
    # Fetching orders for the current user
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


# View for editing user profile
@login_required(login_url='login')
def edit_profile(request):
    try:
        # Trying to get user profile information
        userprofile = UserProfile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        # Handling the case where UserProfile does not exist for the user
        userprofile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        # If the form is submitted
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=userprofile)

        if 'profile_picture' in request.FILES:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            # Saving user and profile form data if valid
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')

    else:
        # If it's a GET request, render profile edit form
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }

    return render(request, 'accounts/edit_profile.html', context)


# View for changing user password
@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        # If the form is submitted
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            # Checking if current password is correct
            success = user.check_password(current_password)
            if success:
                # If current password is correct, updating password
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password Updated Successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current Password')
                return redirect('change_password')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


# View for displaying order details
@login_required(login_url='login')
def order_detail(request, order_id):
    # Fetching order details
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)

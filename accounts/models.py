from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

# Create your models here.

# Custom user manager to handle user creation
class MyAccountManager(UserManager):
    # Method to create a standard user
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username')
        
        # Create a user instance
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)  # Set hashed password
        user.save(using=self._db)    # Save user to the database
        return user

    # Method to create a superuser (admin)
    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True        # Set admin privileges
        user.is_active = True       # Set user as active
        user.is_staff = True        # Set user as staff
        user.is_superadmin = True   # Set as superadmin
        user.save(using=self._db)   # Save user
        return user

# User model extending Django's AbstractUser
class Account(AbstractUser):
    first_name = models.CharField(max_length=50)       # First name of the user
    last_name = models.CharField(max_length=50)        # Last name of the user
    username = models.CharField(max_length=50, unique=True)  # Username, unique
    email = models.EmailField(max_length=100, unique=True)   # Email, unique
    phone_number = models.CharField(max_length=50)     # Phone number of the user

    # Required fields
    date_joined = models.DateTimeField(auto_now_add=True)  # Date of user creation
    last_login = models.DateTimeField(auto_now_add=True)   # Date of last login
    is_admin = models.BooleanField(default=False)          # Is user admin
    is_staff = models.BooleanField(default=False)          # Is user staff
    is_active = models.BooleanField(default=False)         # Is user active
    is_superadmin = models.BooleanField(default=False)     # Is user superadmin

    USERNAME_FIELD = 'email'       # Username field (used for authentication)
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']  # Required fields other than username

    objects = MyAccountManager()   # Custom user manager

    # Method to get full name of the user
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email   # String representation of the user object

    # Check if user has specific permission (admin in this case)
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Check if user has permissions to a given module (always true for now)
    def has_module_perms(self, add_label):
        return True

# Model for additional user profile information
class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)   # Link to the user
    address_line_1 = models.CharField(blank=True, max_length=100)    # Address line 1
    address_line_2 = models.CharField(blank=True, max_length=100)    # Address line 2
    profile_picture = models.ImageField(blank=True, upload_to='userprofile')  # Profile picture
    city = models.CharField(blank=True, max_length=20)               # City
    state = models.CharField(blank=True, max_length=20)              # State
    country = models.CharField(blank=True, max_length=20)            # Country

    def __str__(self):
        return self.user.first_name   # String representation of the user's first name

    # Method to get full address of the user
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'  # Combine address lines

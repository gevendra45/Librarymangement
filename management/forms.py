from django import forms 
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm): 
    """
    Formdata from user registration form is fetched and validated
    """
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    class Meta: 
        model = User 
        fields = ['username', 'email', 'password1' , 'first_name' , 'last_name'] 
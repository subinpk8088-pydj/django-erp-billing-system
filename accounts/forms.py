from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser

class UserRegisterForm(UserCreationForm):

    username = forms.CharField(
        max_length=30
    )

    class Meta:

        model = CustomUser

        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'role',
            'password1',
            'password2'
        ]
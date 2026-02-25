from django import forms
from django.contrib.auth import get_user_model

from .models import Profile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "avatar"]

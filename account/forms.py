from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def validate_email(value):
    if User.objects.filter(email = value).exists():
        raise ValidationError((f"{value} is taken."), params={"value":value})

class CreateUserForm(UserCreationForm): #inherits usercreationform
    username = forms.CharField(widget=forms.TextInput(attrs={"class":"input", "type":"username", "placeholder":"enter username"}), label="Username")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class":"input", "type":"email", "placeholder":"enter email"}), label = "Email", validators=[validate_email])
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class":"input", "type":"password", "placeholder":"enter password"}), label = "Enter password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class":"input", "type":"password", "placeholder":"re-enter password"}), label="Re-enter password")

    class Meta: #must be inside class
        model = User
        fields = ["username", "email", "password1", "password2"] 


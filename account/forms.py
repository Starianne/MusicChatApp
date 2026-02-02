from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class CreateUserForm(UserCreationForm): #inherits usercreationform
    username = forms.CharField(widget=forms.TextInput(attrs={"class":"input", "type":"text", "placeholder":"enter username"}), label="Username")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class":"input", "type":"email", "placeholder":"enter email"}), label = "Email")
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class":"input", "type":"password", "placeholder":"enter password"}), label = "Enter password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class":"input", "type":"password", "placeholder":"re-enter password"}), label="Re-enter password")

    class Meta: #must be inside class
        model = User
        fields = ["username", "email", "password1", "password2"] 
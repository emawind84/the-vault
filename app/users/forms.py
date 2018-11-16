from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserChangeForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password2"].required = False

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
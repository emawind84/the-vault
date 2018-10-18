from django import forms
from django.contrib.auth.models import User

from .models import Secret

def generate_password():
    random_password = User.objects.make_random_password(allowed_chars='abcdefghjkmnpqrstuvwxyz'
        'ABCDEFGHJKLMNPQRSTUVWXYZ'
        '23456789!@#$%&')
    
    return random_password
    
class SecretForm(forms.ModelForm):
    random_password = generate_password()
    password = forms.CharField(widget=forms.PasswordInput, required=False, initial=random_password)
    notes = forms.CharField(widget=forms.Textarea(attrs={'cols': 80}), required=False)
    url = forms.CharField(required=False, label="Domain")
    ip = forms.CharField(required=False, label="IP")
    confirm_password=forms.CharField(widget=forms.PasswordInput(), required=False, label="Repeat password", initial=random_password)
    
    field_order = ['label', 'category', 'username', 'password', 'confirm_password', 'ip', 'url', 'project', 'config', 'notes', 'groups']

    class Meta:
        model = Secret
        fields = ['label', 'username', 'password', 'url', 'notes', 'category', 'ip', 'config', 'project', 'groups']
        #labels = {'url': 'URL'}

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match.")

        # this is used for checking duplicates if the attribute unique=True is not used
        # matching_secrets = Secret.objects.filter(label=cleaned_data.get("label"))
        # if self.instance:
        #     matching_secrets = matching_secrets.exclude(pk=self.instance.pk)

        # if matching_secrets.exists():
        #     msg = "A secret with this label already exists."
        #     self.add_error('label', msg)
        return self.cleaned_data
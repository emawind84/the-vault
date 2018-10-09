from django import forms

from .models import Secret

class SecretForm(forms.ModelForm):
    username = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'cols': 80}), required=False)
    url = forms.URLField(required=False, label="Website")
    confirm_password=forms.CharField(widget=forms.PasswordInput(), required=False, label="Repeat password")
    
    field_order = ['label', 'category', 'username', 'password', 'confirm_password', 'url', 'project', 'config', 'notes']

    class Meta:
        model = Secret
        fields = ['label', 'username', 'password', 'url', 'notes', 'category']
        #labels = {'url': 'URL'}

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match.")

        """
        # this is used for checking duplicates if the attribute unique=True is not used
        matching_secrets = Secret.objects.filter(label=cleaned_data.get("label"))
        if self.instance:
            matching_secrets = matching_secrets.exclude(pk=self.instance.pk)

        if matching_secrets.exists():
            msg = "A secret with this label already exists."
            self.add_error('label', msg)
        """
        return self.cleaned_data

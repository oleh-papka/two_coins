from django import forms
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm

from core.mixins.forms import BootstrapFormMixin
from users.models import User


class UserAddForm(BootstrapFormMixin, BaseUserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
        field_classes = {'email': forms.EmailField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()

        self.fields["email"].widget.attrs |= {'autocomplete': 'email', 'autofocus': True}
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"


class CustomAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()

        self.fields["username"].widget.attrs["autocomplete"] = "email"
        self.fields["password"].widget.attrs["autocomplete"] = "current-password"


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

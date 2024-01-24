from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from users.models import Company

# class RegForm()

User = get_user_model()


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    password1 = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')


class CompanyCreationForm(ModelForm):
    class Meta:
        model = Company
        exclude = ['user']

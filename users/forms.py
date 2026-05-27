from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from users.models import User
from users.validators import validate_phone, validate_github_url


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Придумайте пароль"}),
        min_length=6,
    )

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Имя"}),
            "surname": forms.TextInput(attrs={"placeholder": "Фамилия"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email", "autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Пароль"}),
    )

    @property
    def email(self):
        return self["username"]


class ProfileEditForm(forms.ModelForm):
    phone = forms.CharField(
        label="Телефон",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+7XXXXXXXXXX"}),
    )
    github_url = forms.URLField(
        label="GitHub",
        required=False,
        validators=[validate_github_url],
        widget=forms.URLInput(attrs={"placeholder": "https://github.com/username"}),
    )

    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Имя"}),
            "surname": forms.TextInput(attrs={"placeholder": "Фамилия"}),
            "about": forms.Textarea(
                attrs={"placeholder": "Расскажите о себе", "rows": 3}
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if phone:
            return validate_phone(phone)
        return phone


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(),
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(),
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(),
    )

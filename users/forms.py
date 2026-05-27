import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from core.constants import PHONE_PATTERN, USER_NAME_MAX_LENGTH
from core.validators import validate_github_url

User = get_user_model()


class RegisterForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=USER_NAME_MAX_LENGTH)
    surname = forms.CharField(label="Фамилия", max_length=USER_NAME_MAX_LENGTH)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self):
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
        )


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный email или пароль")
            cleaned_data["user"] = user
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            raise forms.ValidationError("Укажите номер телефона.")
        if not re.fullmatch(PHONE_PATTERN, phone):
            raise forms.ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")
        if phone.startswith("8"):
            phone = "+7" + phone[1:]

        same_phone = User.objects.filter(phone=phone).exclude(pk=self.instance.pk)
        if same_phone.exists():
            raise forms.ValidationError("Пользователь с таким телефоном уже существует.")
        return phone

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url"))

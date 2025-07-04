import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    username = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean_username(self):
        """Проверка на пустое поле username и минимальную длину"""
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("Пустое поле")
        if len(username) < 3:
            raise ValidationError("Хотя бы больше 3 символов")
        return username

    def clean_password(self):
        """Проверка на пустое поле password и соответствие условиям"""
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("Пустое поле")
        if not re.match(r'^[a-zA-Z0-9]*$', password):
            raise ValidationError("Пароль может содержать только латинсик символы и цифры")
        return password

from django import forms
from django.core.exceptions import ValidationError
from .models import Biblioteka
from django.contrib.auth.models import User


class AddPostForm(forms.Form):
    title = forms.CharField(max_length=32)
    author = forms.CharField(max_length=32)
    price = forms.IntegerField()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, label='Имя пользователя')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise ValidationError('Пароли не совпадают')

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email


class CartItemForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label='Количество')
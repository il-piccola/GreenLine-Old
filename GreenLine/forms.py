import re
from django import forms
from django.forms import ModelForm
from .models import *

def make_password() :
    ret = ''
    while not re.match(r'[0-9]+', ret) :
        l = list('0123456789abcdefghijklmnopqrstuvwxyz')
        random.shuffle(l)
        s = ''.join(l)
        ret = s[0:7]
    return ret

class LoginForm(forms.ModelForm) :
    phone = forms.CharField(label="電話番号", widget=forms.TextInput(attrs={'class':'form-control', 'pattern':'^[0-9]+$'}))
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput(attrs={'class':'form-control'}))
    class Meta :
        model = Employee
        fields = ['phone', 'password', ]

class MainForm(forms.Form) :
    phone = forms.CharField(label="電話番号", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'01234567890', 'pattern':'^[0-9]+$'}))

class PasswordForm(forms.Form) :
    old = forms.CharField(label="旧パスワード", widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new = forms.CharField(label="新パスワード", widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirm = forms.CharField(label="新パスワード(確認)", widget=forms.PasswordInput(attrs={'class':'form-control'}))

class EmployeeForm(forms.ModelForm) :
    organization = forms.ModelChoiceField(label="所属", queryset=Organization.objects, to_field_name='name', widget=forms.Select(attrs={'class':'form-select'}))
    name = forms.CharField(label="氏名", widget=forms.TextInput(attrs={'class':'form-control'}))
    kana = forms.CharField(label="カナ", widget=forms.TextInput(attrs={'class':'form-control', 'pattern':'^[ァ-ヴ]+$'}))
    phone = forms.CharField(label="電話番号", widget=forms.TextInput(attrs={'class':'form-control', 'pattern':'^[0-9]+$'}))
    password = forms.CharField(label="パスワード", initial=make_password(), widget=forms.TextInput(attrs={'class':'form-control', 'disabled':'disabled'}))
    auth = forms.BooleanField(label="管理者権限", required=False, widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    confirm = False
    class Meta :
        model = Employee
        fields = ['organization', 'name', 'kana', 'phone', 'password', 'auth', ]
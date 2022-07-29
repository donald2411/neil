from django import forms
from django.core.mail import send_mail
import logging
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from . import models
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import authenticate


logger = logging.getLogger(__name__)
class ContactForm(forms.Form):
    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField()

    def send_mail(self):
        logger.info('Sending email to customer service')
        message = "From:{0}\n{1}".format(self.cleaned_data['name'],self.cleaned_data['message'])

        send_mail(
            "Site Message",
            message,
            "site@forexpro.domain",
            ["customerservice@forexpro.domain"],
            fail_silently=False
        )
    
class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ['email','full_name','username','country','phonenumber']
        field_classes = {'email':UsernameField}

    def send_mail(self):
        logger.info('sending Mail to Customer')
        message = "Welcome {0}, ".format(self.cleaned_data['email'])

        send_mail(
            "Welcome to ForexPro",
            message,
            "site@forexpro.domain",
            [self.cleaned_data['email'],],
            fail_silently=True
        )

class AuthenticateForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(),strip=False)
    def __init__(self,request = None,*args,**kwargs):
        self.request = request
        self.user = None
        super().__init__(*args,**kwargs)
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email is not None and password:
            self.user = authenticate(self.request,email=email,password=password)
        if self.user is None:
            raise forms.ValidationError('Incorrect Email/Password')
        logger.info('Authentication successful for email "%s"'%email)
        return self.cleaned_data
    def get_user(self):
        return self.user

class DepositForm(forms.ModelForm):
    class Meta:
        model = models.Deposit
        exclude = ['user','status']

class WithdrawForm(forms.ModelForm):
    class Meta:
        model = models.Withdraw
        exclude = ['user','status']

class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["full_name","email","phonenumber","country","username"]
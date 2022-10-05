
import random
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, UpdateView

from core.models import Account, Deposit, User, Withdraw, Settings
from . import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.core.mail import send_mail
from django.http import JsonResponse


#helper function
def send_login_verification_mail(email,token):
    send_mail(
    "Login Request",
    f'You have requested to Login from coinface.\nif these was not you kindly ignore this mail or contact support.\nVerification Token: {token}',
    from_email="support@coinface.us",
    recipient_list=[email],
    fail_silently=False
    )
def send_withdrawal_verification_mail(email,token):
    send_mail(
    "Withdrawal Request",
    f'You have requested a Withdrawal from your account in coinface.\nif these was not you kindly ignore this mail or contact support.\nVerification Token: {token}',
    from_email="support@coinface.us",
    recipient_list=[email],
    fail_silently=False)
def generate_token():
    verification_token = random.randint(100000,999999)
    return verification_token


# Create your views here.
class ContactView(FormView):
    template_name = 'contact.html'
    form_class =  forms.ContactForm
    success_url = '/contact'
    def form_valid(self,form):
        form.send_mail()
        messages.success(self.request,"Message Sent")
        return super().form_valid(form)

logger = logging.getLogger(__name__)
class RegisterView(FormView):
    template_name = 'register.html'
    form_class = forms.UserCreationForm
    success_url = '/dashboard/'
    def get_success_url(self):
        redirect_to = self.request.GET.get('next','/dashboard/')
        return redirect_to
    def form_valid(self,form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        logger.info('New SignUp for %s through SignUpView'%email)
        user = authenticate(email = email, password = password)
        form.send_mail()
        login(self.request,user)
        messages.info(self.request,'You signed up Successfully')
        return response

class DashboardView(LoginRequiredMixin, View):
    def get(self,request):
        account = Account.objects.get(user = request.user)
        return render(request, 'dashboard/dashboard.html',{'account':account})


class ProfileView(LoginRequiredMixin, View):
    def get(self,request):
        return render(request, 'dashboard/profile.html')
class DepositFormView(LoginRequiredMixin, FormView):
    form_class = forms.DepositForm
    success_url = '/fund/'
    template_name = "dashboard/fund.html"
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        deposits = Deposit.objects.filter(user = self.request.user)
        context['deposits'] = deposits
        address = 'no set'
        wallet_address = Settings.objects.filter(name = 'btc' )
        if wallet_address:
            address = wallet_address[0].value
        context['address'] = address
        return context
    def form_valid(self, form):
        obj = form.save(commit = False)
        obj.user = self.request.user
        obj.save()
        messages.success(self.request,"Deposit Request Sent")
        return super().form_valid(form)
class WithdrawFormView(LoginRequiredMixin, FormView):
    form_class = forms.WithdrawForm
    success_url = '/withdraw/'
    template_name = "dashboard/withdraw.html"
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        withdraws = Withdraw.objects.filter(user = self.request.user)
        account = Account.objects.get(user = self.request.user)
        context['withdraws'] = withdraws
        context['account'] = account
        return context
    def form_valid(self, form):
        obj = form.save(commit = False)
        obj.user = self.request.user
        obj.save()
        if "withdraw_token" in self.request.session:
            del self.request.session['withdraw_token']
        messages.success(self.request,"Withdrawal Request Sent")
        return super().form_valid(form)

class VerifyWithdrawal(LoginRequiredMixin,View):
    def post(self,request):
        if not request.is_ajax():
            messages.error(request,"Improperly configured request")
            return redirect(reverse("withdraw"))
        email = request.user.email
        token = generate_token()
        send_withdrawal_verification_mail(email,token)
        request.session["withdraw_token"] = token
        return JsonResponse({"status":True})


class LoginView(FormView):
    form_class = forms.AuthenticateForm
    template_name = "login.html"
    success_url = reverse_lazy("verify-login")

    def form_valid(self, form):
        user = form.get_user()
        token = generate_token()
        send_login_verification_mail(user.email,token)
        self.request.session['login_token'] = token
        self.request.session['user'] = user.email
        messages.success(self.request,"A verification token has been sent to your email address.")
        
        return super().form_valid(form)


class VerifyLoginView(View):
    def get(self,request):
        if not "login_token" in request.session:
            return redirect(reverse("login"))
        return render(request,"verify-login.html")
    def post(self,request):
        if not "login_token" in request.session:
            return redirect(reverse("login"))
        token = request.POST['token']
        login_token = request.session['login_token']
        userEmail = request.session['user']
        if token == str(login_token):
            messages.success(request,"Login Successful")
            login(request,User.objects.get(email = userEmail))
            del request.session['user']
            del request.session['login_token']
            return redirect(reverse("dashboard"))
        else:
            # messages.error(request,"Invalid Token")
            return render(request,"verify-login.html",{"error":"Invalid Token"})

class ResendVerificationMailView(View):
    def get(self,request):
        if not "login_token" in request.session or not "user" in request.session:
            return redirect(reverse("login"))
        email = request.session['user']
        token = request.session['login_token']
        send_login_verification_mail(email, token)
        messages.success(self.request,"A verification token has been sent to your email address.")
        return redirect(reverse("verify-login"))

class LogoutView(LoginRequiredMixin, View):
    def get(self,request):
        logout(request)
        messages.success(request, "Logout Successful")
        return redirect('/login/')


class EditProfileView(LoginRequiredMixin,View):
    def get(self, request):
        userform = forms.UserForm(instance=request.user)
        passwordform = PasswordChangeForm(user= request.user)
        context = {
            "userform":userform,
            "passwordform":passwordform,
        }
        return render(request, "dashboard/edit-profile.html",context)
    def post(self,request):
        userform = forms.UserForm(instance=request.user)
        passwordform = PasswordChangeForm(user= request.user)
        
        if request.POST.get('submit') == "save":
            userform = forms.UserForm(instance=request.user,data = request.POST)
            if userform.is_valid():
                userform.save()
                messages.success(request,"Profile Updated")
                return redirect('/profile/edit/')
        elif request.POST.get('submit') == "update":
            passwordform = PasswordChangeForm(request.user,request.POST)
            if passwordform.is_valid():
                passwordform.save()
                messages.success(request,"Password Updated")
                update_session_auth_hash(request,passwordform.user)
                return redirect('/profile/edit/')
        context = {
            "userform":userform,
            "passwordform":passwordform,
        }
        return render(request, "dashboard/edit-profile.html",context)

class DeleteAccountView(LoginRequiredMixin, View):
    def post(self,request):
        password = request.POST.get('password')
        if not password:
            return redirect('/profile/')
        user = User.objects.get(id = request.user.id)
        valid_password = user.check_password(password)
        if valid_password:
            logout(request)
            logger.info('Deleting Account of %s through DeleteAccountView'%user.email)
            user.is_active = False
            user.save()
            messages.success(request,"Account Deleted")
            return redirect('/')
        messages.error(request,"Invalid Password")
        return redirect('/profile/edit/')






"""
Error Handlers
"""



def handler_404(request,exception):
    return render(request,"404.html", status=404)
def handler_403(request,exception):
    return render(request,"403.html")

def handler_500(request):
    return render(request,"500.html")
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model, authenticate, login as dj_login, logout as s_logout
from django.contrib.auth import user_logged_in
from django.dispatch.dispatcher import receiver
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from setup.settings import EMAIL_FROM
from django.db.models import Sum
User = get_user_model()


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password)
        if user is not None:
            dj_login(request, user)
            request.session.set_expiry(1200)
            return redirect('/home')
        else:
            messages.error(request, "Invalid Login Details")
            return redirect('/')
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == "POST":
        fullname = request.POST['fullname']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already taken")
                return redirect('/register')
            else:
                user = User.objects.create_user(fullname=fullname, email=email, password=password1)
                user.save()
                messages.success(request, "Registration Successful")
                return redirect('/')
        else:
            messages.error(request, "Password not match")
            return redirect('/register')
    else:
        return render(request, 'register.html')


def logout(request):
    s_logout(request)
    messages.success(request, "Logout Successfully")
    return redirect('/')


@login_required(login_url='/')
def home(request):
    return render(request, 'index.html')


@login_required(login_url='/')
def compose(request):
    if request.method == "POST":
        to_email = request.POST['to_email']
        subject = request.POST['subject']
        message = request.POST['message']

        email_list = to_email.split(',')
        for data in email_list:
            print(data)
            subject, from_email, to = 'New Registration', EMAIL_FROM, data
            html_content = render_to_string('mail/mail.html', {'message': message})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        print(email_list)
    return render(request, 'compose.html')
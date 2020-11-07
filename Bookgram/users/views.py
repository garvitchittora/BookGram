from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.shortcuts import render, redirect
from django.contrib import messages

from .models import *

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .tokens import account_activation_token

def getUserWithSimilarBook(user):
    userAll= User.objects.all()
    similarUser=[]
    for book in user.books.all():
        isbn=book.isbn
        for u in userAll:
            if u.books.filter(isbn=isbn).count()>0 and not ( u in similarUser) and not (u == user ):
                similarUser.append(u)

    return similarUser        

def home(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    else:
        x = ""
        user= request.user
        recommendedUsers = getUserWithSimilarBook(user)
        if request.method == 'POST':
            x = request.POST["name"]
            
        return render(request, "index.html",{"string":x,"user":user,"recommendedUsers":recommendedUsers})

def login(request):
    if request.user.is_authenticated:
        messages.add_message(request, messages.SUCCESS, 'User Successfully registered')
        return redirect('/') 
    else:
        if request.method == 'POST':
            password=request.POST['password']
            email=request.POST['email']

            user = authenticate(username=email, password=password)
            if user:
                auth_login(request, user)
                return redirect("/")
            else:
                messages.add_message(request, messages.SUCCESS, 'Incorrect Email Or Password')
               
        return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    return redirect("/login")

def register(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == 'POST':
            email=request.POST['email']

            password1=request.POST['password1']
            print(password1)
            password2=request.POST['password2']

            if password2 == password1:
                if email and User.objects.filter(email=email).exists():
                    messages.add_message(request, messages.ERROR, 'Email addresses must be unique.')
                else:
                    user = User(email=email)
                    user.set_password(password1)  
                    if request.POST.get('first',False):
                        user.first_name=request.POST['first']

                    if request.POST.get('second',False):
                        user.last_name=request.POST['second']

                    if request.FILES.get('image'):
                        user.image = request.FILES.get('image')
                        
                    user.is_active = False
                    user.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Activate your BookGarm account.'
                    html_message = render_to_string('acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                        'token':account_activation_token.make_token(user),
                    })

                    to_email = email
                    email = EmailMessage(
                                mail_subject, html_message, to=[to_email]
                    )
                    email.content_subtype = "html"
                    email.send()
                    return render(request, 'emailComplete.html')
            else:
                messages.add_message(request, messages.ERROR, 'Both password doesnot match.')
        
        return render(request, 'register.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        return redirect("/")        
    else:
        return render(request, 'invalidEmail.html') 

def userProfile(request,slug):
    print(slug)
    
    return render(request, "userProfile.html",{})

def bookPage(request,slug):
    print(slug)
    x = ""
    if request.method == 'POST':
        x = request.POST["name"]
        
    
    return render(request, "index.html",{"string":x})

def searchUser(request):
    x = ""
    if request.method == 'POST':
        x = request.POST["name"]
        
    
    return render(request, "index.html",{"string":x})    

def searchBook(request):
    x = ""
    if request.method == 'POST':
        x = request.POST["name"]
        
    
    return render(request, "index.html",{"string":x})  
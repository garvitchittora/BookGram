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
import requests
import json
# from .ml import recom_list_combined

def getUserWithSimilarBook(user):
    userAll= User.objects.all()
    similarUser=[]
    for book in user.books.all():
        bookid=book.bookid
        for u in userAll:
            if u.books.filter(bookid=bookid).count()>0 and not ( u in similarUser) and not (u == user ):
                similarUser.append(u)

    return similarUser        

def home(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    else:
        x = ""
        user= request.user
        recommendedUsers = getUserWithSimilarBook(user)

        books = user.books.all()
        if request.method == 'POST':
            if request.POST["formid"]=="1":
                bookid=request.POST["id"]
                title=request.POST["title"]     
                if books.filter(bookid=bookid).count()==0:
                    book=Book(title = title,bookid=bookid)
                    book.save()
                    user.books.add(book)
                    user.save()
            else:
                if User.objects.filter(id=request.POST["id"]).count()>0:
                    fuser = User.objects.filter(id=request.POST["id"]).first()
                    user=request.user
                    user.followers.add(fuser)
                    user.save()

        books = user.books.all()

        listName=[]
        for book in books:
            listName.append(book.title)
        
        # recom_book = recom_list_combined(listName)
        
        dataBook=[]
        # if recom_book and len(recom_book)>0:
        #     for book in recom_book:
        #         data=requests.get("https://www.googleapis.com/books/v1/volumes?q="+book).json()
        #         if "items" in data:
        #             data=data["items"]
        #             if len(data)>=0 :
        #                 data=data[0]
        #                 obj={"name":"","authors":"","image":"https://yobafit.com/static/img/icons/0000.png","bookid":"","rating":"0"}
        #                 obj["name"]=data["volumeInfo"]["title"]
        #                 obj["bookid"]=data["id"]
        #                 if  "authors" in data["volumeInfo"]:
        #                     obj["authors"]=data["volumeInfo"]["authors"]
        #                 if "imageLinks" in data["volumeInfo"]:
        #                     obj["image"]=data["volumeInfo"]["imageLinks"]["thumbnail"]
        #                 if 'averageRating' in data["volumeInfo"]:
        #                     obj["rating"]=str(data["volumeInfo"]["averageRating"])
        #                 dataBook.append(obj)

        return render(request, "index.html",{"string":x,"user":user,"recommendedUsers":recommendedUsers,"recom_book":dataBook})

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
    if request.user.is_authenticated:
        user=request.user
        name=user.get_full_name()
        followersNumber=user.followers.count()
        followingNumber=user.user_set.all().count()
        posts = user.post_set.all() 
        books = user.books.all() 

        if request.method == 'POST':
            bookid=request.POST["id"]
            title=request.POST["title"]     
            if books.filter(bookid=bookid).count()==0:
                book=Book(title = title,bookid=bookid)
                book.save()
                user.books.add(book)
                user.save()

        books = user.books.all() 
        dataPosts=[]
        for post in posts:
            data=requests.get("https://www.googleapis.com/books/v1/volumes?q="+post.bookid).json()
            if "items" in data:
                data=data["items"]
                if len(data)>=0 :
                    data=data[0]
                    obj={"name":"","authors":"","image":"https://yobafit.com/static/img/icons/0000.png","caption":post.caption,"bookid":post.bookid,"rating":"0"}
                    obj["name"]=data["volumeInfo"]["title"]
                    if  "authors" in data["volumeInfo"]:
                        obj["authors"]=data["volumeInfo"]["authors"]
                    if "imageLinks" in data["volumeInfo"]:
                        obj["image"]=data["volumeInfo"]["imageLinks"]["thumbnail"]
                    if 'averageRating' in data["volumeInfo"]:
                        obj["rating"]=str(data["volumeInfo"]["averageRating"])
                    dataPosts.append(obj)
        
        dataBook=[]
        for book in books:
            data=requests.get("https://www.googleapis.com/books/v1/volumes?q="+book.bookid).json()
            if "items" in data:
                data=data["items"]
                if len(data)>=0 :
                    data=data[0]
                    obj={"name":"","authors":"","image":"https://yobafit.com/static/img/icons/0000.png","bookid":post.bookid,"rating":"0"}
                    obj["name"]=data["volumeInfo"]["title"]
                    if  "authors" in data["volumeInfo"]:
                        obj["authors"]=data["volumeInfo"]["authors"]
                    if "imageLinks" in data["volumeInfo"]:
                        obj["image"]=data["volumeInfo"]["imageLinks"]["thumbnail"]
                    if 'averageRating' in data["volumeInfo"]:
                        obj["rating"]=str(data["volumeInfo"]["averageRating"])
                    dataBook.append(obj)

        return render(request, "userProfile.html",{"name":name,"followersNumber":followersNumber,"followingNumber":followingNumber,"dataPosts":dataPosts,"dataBook":dataBook})
    else:
        return redirect("/login")     

def bookDetails(request,slug):
    data=requests.get("https://www.googleapis.com/books/v1/volumes?q="+slug).json()
    if request.method == 'POST':
        bookid=request.POST["id"]
        title=request.POST["title"]  
        user= request.user
        books = user.books.all()   
        
        if books.filter(bookid=bookid).count()==0:
            book=Book(title = title,bookid=bookid)
            book.save()
            user.books.add(book)
            user.save()

    if "items" in data:
        data=data["items"]
        if len(data)>=0 :
            data=data[0]
            obj={"name":"","authors":"","image":"https://yobafit.com/static/img/icons/0000.png","bookid":slug,"rating":"0","pageCount":"0","description":"","publishedDate":"","publisher":""}
            obj["name"]=data["volumeInfo"]["title"]
            if  "authors" in data["volumeInfo"]:
                obj["authors"]=data["volumeInfo"]["authors"]
            if "imageLinks" in data["volumeInfo"]:
                obj["image"]=data["volumeInfo"]["imageLinks"]["thumbnail"]
            if 'averageRating' in data["volumeInfo"]:
                obj["rating"]=str(data["volumeInfo"]["averageRating"])
            if  "pageCount" in data["volumeInfo"]:
                obj["pageCount"]=data["volumeInfo"]["pageCount"]
            if  "description" in data["volumeInfo"]:
                obj["description"]=data["volumeInfo"]["description"]        
            if  "publishedDate" in data["volumeInfo"]:
                obj["publishedDate"]=data["volumeInfo"]["publishedDate"]  
            if  "publisher" in data["volumeInfo"]:
                obj["publisher"]=data["volumeInfo"]["publisher"]  

    listrecom=[]
    listrecom.append(obj["name"])
    recom_book = recom_list_combined(listrecom)

    dataBook=[]
    if recom_book and len(recom_book)>0:
        for book in recom_book:
            data=requests.get("https://www.googleapis.com/books/v1/volumes?q="+book).json()
            if "items" in data:
                data=data["items"]
                if len(data)>=0 :
                    data=data[0]
                    ob={"name":"","authors":"","image":"https://yobafit.com/static/img/icons/0000.png","bookid":"","rating":"0"}
                    ob["name"]=data["volumeInfo"]["title"]
                    ob["bookid"]=data["id"]
                    if  "authors" in data["volumeInfo"]:
                        ob["authors"]=data["volumeInfo"]["authors"]
                    if "imageLinks" in data["volumeInfo"]:
                        ob["image"]=data["volumeInfo"]["imageLinks"]["thumbnail"]
                    if 'averageRating' in data["volumeInfo"]:
                        ob["rating"]=str(data["volumeInfo"]["averageRating"])
                    dataBook.append(ob)

    return render(request, "bookdetails.html",{"dataBook":dataBook,"obj":obj})

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
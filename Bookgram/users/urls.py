from django.urls import path, include
from .views import home, login, register, userProfile, bookPage, searchUser, searchBook, activate
# from django.conf.urls import url

urlpatterns = [
    path('', home,name="home"),
    path('login/', login,name="login"),
    path('register/', register,name="register"),
    path('user/<slug:slug>', userProfile,name="userProfile"),
    path('book/<slug:slug>', bookPage,name="bookPage"),
    path('searchuser/', searchUser,name="searchUser"),
    path('searchbook/', searchBook,name="searchBook"),
    path('activate/<uidb64>/<token>/',activate, name='activate'), 
]
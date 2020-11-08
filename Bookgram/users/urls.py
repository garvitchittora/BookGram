from django.urls import path, include
from .views import home, login, register, userProfile, bookDetails, searchUser, searchBook, activate, logout, compose
# from django.conf.urls import url

urlpatterns = [
    path('', home,name="home"),
    path('login/', login,name="login"),
    path('logout/', logout,name="logout"),
    path('register/', register,name="register"),
    path('user/<slug:slug>', userProfile,name="userProfile"),
    path('book/<slug:slug>', bookDetails,name="bookDetails"),
    path('searchuser/', searchUser,name="searchUser"),
    path('search/', searchBook,name="searchBook"),
    path('activate/<uidb64>/<token>/',activate, name='activate'), 
    path('compose/', compose,name="compose"),
]
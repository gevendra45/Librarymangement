from .models import *
from .serializers import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import json
import requests
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from oauth2_provider.models import Application, AccessToken, RefreshToken
from rest_framework import permissions

import pytz
from datetime import datetime, timedelta

from .forms import UserRegisterForm
from django.contrib.auth.models import User

import string
import secrets
from django.core.mail import send_mail, EmailMultiAlternatives

from django.shortcuts import render

from oauthlib.oauth2.rfc6749.tokens import random_token_generator
from library.settings import OAUTH2_PROVIDER

import re

def home(request):
    return render(request, "home.html")


@api_view(["POST", ])
def addbooksauthor(request):
    """
    url -> /add/book/author/
    DataFormat -> {
        "books"  : [{
            "book_name":"Goblet of fire",
            "publish_date":"2007-08-20"
        },
        {
            "book_name":"Harry Potter",
            "publish_date":"2001-07-15"
        }],
        "authors":[{
            "author_name":"J. K. Rowling",
            "address":"Paris",
            "phone_no":"947289439"
        },
        {
            "author_name":"Rober Kiyosaki",
            "address":"London",
            "phone_no":""
        }]
    }
    """
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    if not request.data["books"] or not request.data["authors"] or type(request.data["authors"]) != list or type(request.data["books"]) != list:
        return Response(status=400, data = "Parameters are missing from the request.")
    
    result = []
    books=[]
    authors=[]

    try:
        for i in request.data['books']:
            serializer = Book_Serialize(data=i)
            if serializer.is_valid():
                if serializer.avialable():
                    serializer.save()
                    result.append({
                            'book name' : i['book_name'], 
                            'status'    : 'Book has been added successfully.'
                        })
                else:
                    result.append({
                            'book name' : i['book_name'], 
                            'status'    : "Book with same details present in database."
                        })
                books.append(Book.objects.get(book_name = i['book_name'].title()))
            else:
                result.append({
                        'book name' : i['book_name'], 
                        'status'    : 'Invalid details provided for books'
                    })

        for i in request.data['authors']:
            serializer = Author_Serialize(data=i)
            if serializer.is_valid():
                if serializer.avialable():
                    serializer.save()
                    result.append({
                            'author name' : i['author_name'],
                            'status'      : 'Author has been added successfully.'
                        })
                else:
                    result.append({
                            'author name' : i['author_name'], 
                            'status'      : "Author with same details present in database."
                        })
                authors.append(Author.objects.get(author_name = i['author_name'].title()))
            else:
                result.append({
                        'author name' : i['author_name'], 
                        'status'      : 'Invalid details provided for Author'
                    })
        for book in books:
            for author in authors:
                book.authors.add(author)
                book.save()
    except Exception as e:
        return Response(status=400, data={'msg':'Error while adding Books and Author.'})
    else:
        return Response(status=200, data=result)


@api_view(["POST", ])
def addcategorybooks(request):
    """
    url -> /add/category/book/
    DataFormat -> {
            "category":["Science", "Thrill"],
            "books" : ["rich dad poor dad", "harry potter", "goblet of fire"]
        }
    """
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    if not request.data["books"] or not request.data["category"] or type(request.data["category"]) != list or type(request.data["books"]) != list:
        return Response(status=400, data = "Parameters are missing from the request.")
    result = []
    category=[]
    try:
        for i in request.data['category']:
            serializer = Category_Serialize(data={ "category_name" : i })
            if serializer.is_valid():
                if serializer.avialable():
                    serializer.save()
                    result.append({
                            'category name' : i,
                            'status'      : 'Category has been added successfully.'
                        })
                else:
                    result.append({
                            'category name' : i,
                            'status'      : "Category with same details present in database."
                        })
                category.append(Categories.objects.get(category_name = i.title()))
            else:
                result.append({
                        'category name' : i,
                        'status'      : 'Invalid details provided for Category'
                    })

        books=[]
        for i in request.data["books"]:
            try:
                book=Book.objects.get(book_name = i.title())
            except Exception as e:
                result.append({
                        'book name' : i, 
                        'status'    : i+' is not present in DB'
                    })
            else:
                books.append(book)
        for cat in category:
            for book in books:
                cat.book_belongs.add(book)
                book.save()
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'msg':'Error while adding Category to database.'})
    else:
        return Response(status=200, data=result)


@api_view(["GET", ])
def bookdetials(request):
    """
    url -> /book/detials/
    Response Format -> {
        "author_name": ""
    }
    """
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    book=Book.objects.all()
    result=[]
    for b in book:
        temp={}
        temp['book_name'] = b.book_name
        temp['publish_date'] = b.publish_date
        temp['authors']=[]
        for i in b.authors.all():
            temp['authors'].append({
                'author_name' : i.author_name,
                'address':i.address,
                'phone_no':i.phone_no
                })
        result.append(temp)

    return Response(status=200, data=result)


@api_view(["GET", ])
def authorcount(request, categories_id):
    """
    url -> /api/analytics/author/<categories_id>
    Headers -> {
        Authorization : Bearer JWT_TOKEN
    }
    """
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    try:
        category=Categories.objects.get(id=categories_id).book_belongs.all()
    except Exception as e:
        return Response(status=400, data={'msg':'Category_ID = '+categories_id+" isn't present in database"})
    else:
        res=set([])
        for cat in category:
            for auth in cat.authors.all():
                res.add(auth.author_name)

        return Response(status=200, data={'total_authors' : len(res)})


@api_view(["GET", ])
def bookcount(request, categories_id):
    """
    url -> /api/analytics/books/<categories_id>
    Headers -> {
        Authorization : Bearer JWT_TOKEN
    }
    """
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    try:
        books=Categories.objects.get(id=categories_id).book_belongs.distinct().count()
    except Exception as e:
        return Response(status=400, data={'msg':'Category_ID = '+categories_id+" isn't present in database"})
    else:
        return Response(status=200, data={'total_books' : books})


@api_view(["POST", ])
def login(request):
    """
    url -> /auth/login/
    DataFormat -> {
        "username" : "",
        "password" : "",
    }
    """
    serializer = loginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        if not user.is_active:
            return Response(status=401, data={'Msg': 'No longer access provided'})

        expire_seconds = OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS']
        scopes = OAUTH2_PROVIDER['SCOPES']
        application = Application.objects.get(name="LIBRARY")
        expires = pytz.UTC.localize(datetime.now() + timedelta(seconds=expire_seconds))
        user=User.objects.get(username=request.data['username'])

        access_token = AccessToken.objects.create(
                user=user,
                application=application,
                token=random_token_generator(request),
                expires=expires,
                scope=scopes)

        refresh_token = RefreshToken.objects.create(
                user=user,
                token=random_token_generator(request),
                access_token=access_token,
                application=application)


        res={'access_token' : access_token.token}#response["access_token"]}
        return Response(res)
    else:
        res = serializer.errors
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def logout(request):
    """
    url -> /auth/logout/
    Headers -> {
        Authorization : Bearer JWT_TOKEN
    }
    """
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    try:
        token1=AccessToken.objects.get(token=request.headers['Authorization'][7:])
        token1.delete()

        expired_tokens=AccessToken.objects.filter(expires__lte=pytz.UTC.localize(datetime.now()))
        if len(expired_tokens):
            expired_tokens.delete()

        refresh=RefreshToken.objects.filter(access_token_id = None)
        if len(refresh):
            refresh.delete()

    except Exception as e:
        return Response({'Message': 'Logout Failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'Message': 'Logout Successful'})


@api_view(['POST', ])
def register(request):
    """
    url -> /auth/register/
    DataFormat -> {
        "email" : "",
        "first_name" : "",
        "last_name" : ""
    }
    """
    if not request.data['email'] and not request.data['first_name'] and not request.data['last_name']:
        return Response(status=400, data={'msg':'Parameters missing in the POST requst.'})

    regex = "^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"
    if not (re.search(regex, request.data['email'])):
        return Response(status=400, data={'msg':'Provided email is not valid.'})

    try:
        res = {}
        same_email = User.objects.filter(email=request.data['email'])
        if len(same_email):
            return Response(status=400, data={'msg': 'User already exists with given email address'})
        else:
            form_data = request.data
            form_data['username'] = form_data['email']
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            form_data['password1'] = password
            form_data['password2'] = password
            form = UserRegisterForm(data=form_data)
            res={}
            if form.is_valid():
                user = form.save()

                
                res['Message'] = 'Registerd Successfully'
                res['User'] = {'Email': user.email, 'Registerd_On': user.date_joined}
                res['username'] = user.email
                res['password'] = password

                html_message = """<html><head><title>Welcome to Sams</title></head><body><p style = "font-family:garamond,serif;font-size:16px;">Dear User,</p><p style = "font-family:garamond,serif;font-size:16px;">Thank you for registering on Library application.<br> Please find the below details of your account:</p><div align="center"><table style = "font-family:garamond,serif;font-size:16px;"><td><b>Username </b></td><td>:</td><td>{username}</td><tr><td><b>Password</b></td><td>:</td><td> {password} </b></td></table></div><p style = "font-family:garamond,serif;font-size:16px;">If you have any questions about your account, kindly contact us.</p><p style = "font-family:garamond,serif;font-size:16px;">Regards,<br><b>Team Library</b></p></body></html>""".format(username=user.email, password=password)
                try:
                    send_mail("Welcome to Library, Get yourself started","","noreplyatsolytics@gmail.com",[user.email],fail_silently=True,html_message=html_message)
                except Exception as e:
                    return Response(status=400, data={'Error': "Some error while sending E-mail."})
                return Response(status=200, data=res)
            else:
                res = form.errors
                return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(status=500, data={'msg':'Error while registering the user'})
    else:
        return Response(status=200, data={'Msg': 'User is registered Successfully.'})
from rest_framework import serializers
from .models import Book, Author, Categories
from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class Book_Serialize(serializers.ModelSerializer):
    """
    Serializer for Adding a Book
    """
    class Meta:
        model = Book
        fields = ['book_name', 'publish_date']

    def avialable(self):
        try:
            book = Book.objects.get(
                book_name=self.initial_data['book_name'].title(), 
                publish_date=self.initial_data['publish_date']
            )
        except Exception as e:
            return True
        else:
            return False

    def save(self):
        book_detail = Book(
            book_name = self.initial_data['book_name'].title(),
            publish_date=datetime.strptime(self.initial_data['publish_date'], "%Y-%m-%d")
        )
        book_detail.save()

class Author_Serialize(serializers.ModelSerializer):
    """
    Serializer for Adding an Author
    """
    class Meta:
        model = Author
        fields = ['author_name', 'address', 'phone_no']

    def avialable(self):
        try:
            author = Author.objects.get(
                author_name=self.initial_data['author_name'].title(), 
                address=self.initial_data['address'], 
                phone_no=self.initial_data['phone_no']
            )
        except Exception as e:
            return True
        else:
            return False

    def save(self):
        author_detail = Author(
            author_name = self.initial_data['author_name'].title(),
            address=self.initial_data['address'],
            phone_no=self.initial_data['phone_no']
        )
        author_detail.save()

class Category_Serialize(serializers.ModelSerializer):
    """
    Serializer for Adding an Category
    """
    class Meta:
        model = Categories
        fields = ['category_name']

    def avialable(self):
        try:
            book = Categories.objects.get(
                category_name = self.initial_data['category_name'].title()
            )
        except Exception as e:
            return True
        else:
            return False

    def save(self):
        author_detail = Categories(
            category_name = self.initial_data['category_name'].title()
        )
        author_detail.save()

class loginSerializer(serializers.ModelSerializer):
    """
    Serializer for Login Data
    """
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, data):
        user = authenticate(**data)
        if user:
            return user
        else:
            raise serializers.ValidationError({'Msg': 'Invalid Credentials'})
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from django.core.validators import RegexValidator

class Author(models.Model):
    author_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100, default="India")
    phone_no = models.CharField(max_length=50, default="99******75", validators=[RegexValidator(r'^\d{1,10}$')], null=True, blank=True)

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.author_name


class Book(models.Model):
    book_name = models.CharField(max_length=50, null=True, blank=True)
    publish_date = models.DateField(null=True, blank=True)
    authors = models.ManyToManyField(Author)

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.book_name


class Categories(models.Model):
    category_name = models.CharField(max_length=50)
    book_belongs = models.ManyToManyField(Book)

    class Meta:
        verbose_name = 'Categories'

    def __str__(self):
        return self.category_name
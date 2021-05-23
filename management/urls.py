from django.urls import path, include
from .views import *

app_name = 'Management'

urlpatterns = [

    path('home/', home),

    path('auth/login/', login),
    path('auth/logout/', logout),
    
    path('auth/register/', register),
    
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    path('add/book/author/', addbooksauthor),
    path('add/category/book/', addcategorybooks),
    
    path('book/detials/', bookdetials),
    path('api/analytics/author/<categories_id>', authorcount),
    path('api/analytics/books/<categories_id>', bookcount)

]
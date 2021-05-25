from django.test import Client
from unittest import TestCase, main as unittest_main
from django.contrib.auth.models import User

class SimpleTest(TestCase):

    username=""
    password=""
    token=""

    def setUp(self):
        pass

    def test_a_register(self):
        print("\n\n Testing register as user\n")
        client = Client()
        post_data_clean={
            "email" : "gevendraverma45@gmail.com",
            "first_name" : "Gevendra",
            "last_name" : "Verma"
        }
        response = client.post('/auth/register/', post_data_clean, content_type='application/json')
        self.__class__.username = response.json()['username']
        self.__class__.password = response.json()['password']
        print(response.json())
        self.assertEqual(response.status_code, 200)


    def test_b_login(self):
        print("\n\n Testing login of user\n")
        client = Client()
        response = client.post('/auth/login/', {'username':self.__class__.username, 'password':self.__class__.password})
        self.__class__.token = 'Bearer '+response.json()['access_token']
        print(response.json())
        self.assertEqual(response.status_code, 200)


    def test_c_book_author_addition(self):
        print("\n\n Testing books and authors addition API\n")
        client=Client(HTTP_AUTHORIZATION=self.__class__.token)
        post_data_clean = {
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
        response = client.post('/add/book/author/', post_data_clean, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 200)


    def test_d_book_category_addition(self):
        print("\n\n Testing books and category addition API\n")
        client=Client(HTTP_AUTHORIZATION=self.__class__.token)
        post_data_clean = post_data_clean = {
            "category":["Science", "Thrill"],
            "books" : ["rich dad poor dad", "harry potter", "goblet of fire"]
        }
        response = client.post('/add/category/book/', post_data_clean, content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 200)


    def test_e_book_details(self):
        print("\n\n Testing Books and Author detials API")
        client=Client(HTTP_AUTHORIZATION=self.__class__.token)
        response = client.get('/book/detials/', content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 200)


    def test_f_author_analystics(self):
        print("\n\n Testing number of unique Authors under category 5 API")
        client=Client(HTTP_AUTHORIZATION=self.__class__.token)
        response = client.get('/api/analytics/author/5', content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 200)


    def test_g_book_analytics(self):
        print("\n\n Testing count of unique books under category = 5 API")
        client=Client(HTTP_AUTHORIZATION=self.__class__.token)
        response = client.get('/api/analytics/books/5', content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 200)


    def test_h_book_analytics(self):
        print("\n\n Testing logout API")
        client=Client(HTTP_AUTHORIZATION=self.__class__.token)
        response = client.get('/auth/logout/', content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 200)


    def test_i_deleting_user_created(self):
    	user=User.objects.get(username=self.__class__.username)
    	if user is not None:
    		response=True
    	else:
    		response=False
    	user.delete()
    	self.assertEqual(response, True)


if __name__ == '__main__':
    unittest_main()
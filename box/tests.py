from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
class HomePageTest(TestCase):
    def test_home_page_status_code(self):
        # Make a GET request to the homepage
        response = self.client.get(reverse('box:home'))
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_home_page_template_used(self):
        # Make a GET request to the homepage
        response = self.client.get(reverse('box:home'))
        # Check if the correct template is used for rendering the homepage
        self.assertTemplateUsed(response, 'box/home.html')

    def test_home_page_contains_correct_content(self):
        # Make a GET request to the homepage
        response = self.client.get(reverse('box:home'))
        # Check if the response contains specific content expected on the homepage
        self.assertContains(response, '<h1>Boxing Promotions</h1>', html=True)
        self.assertContains(response, '<p>At Boxing Promotions, we\'re passionate about the sport of boxing and providing a platform for enthusiasts, amateurs, and professionals alike to connect, compete, and celebrate their love for the sweet science.</p>', html=True)
        # Add more content checks as needed



class AccountCreationTest(TestCase):
    def test_account_creation(self):
        # Define test user data
        username = 'testuser'
        email = 'test@example.com'
        password = 'password123'

        # Ensure no user with the same username exists initially
        self.assertFalse(User.objects.filter(username=username).exists())

        # Send a POST request to the account creation endpoint
        response = self.client.post(reverse('account_signup'), {
            'username': username,
            'email': email,
            'password1': password,
            'password2': password
        })

        # Check that the account creation was successful
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        self.assertTrue(User.objects.filter(username=username).exists())

        # Check that the user can log in with the created account
        login_response = self.client.post(reverse('account_login'), {
            'login': username,
            'password': password
        })

        self.assertEqual(login_response.status_code, 302)  # Redirect after successful login
        self.assertIn('_auth_user_id', self.client.session)  # User is logged in

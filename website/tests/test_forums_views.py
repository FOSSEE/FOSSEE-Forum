from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from website.models import Profile, Question, Answer, FossCategory
from forums.forms import *


class AccountRegisterViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')

    def test_view_url_at_desired_location(self):
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('user_register'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('user_register'))
        self.assertTemplateUsed(response, 'forums/templates/user-register.html')

    def test_view_context_form(self):
        response = self.client.get(reverse('user_register'))
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], RegisterForm)

    def test_view_context_SITE_KEY(self):
        response = self.client.get(reverse('user_register'))
        self.assertTrue('SITE_KEY' in response.context)
        self.assertEqual(response.context['SITE_KEY'], settings.GOOGLE_RECAPTCHA_SITE_KEY)

    def test_view_post_context_improper_username(self):
        response = self.client.post(reverse('user_register'),\
                                    {'username': 'johndoe#', 'email': 'admin@example.com',\
                                    'password': 'johndoe1234', 'password_confirm': 'johndoe1234'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'Username required. 5-30 characters. \
                Letters, digits and @/./+/-/_ only.')

    def test_view_post_context_short_username(self):
        response = self.client.post(reverse('user_register'),\
                                    {'username': 'john', 'email': 'admin@example.com',\
                                    'password': 'johndoe1234', 'password_confirm': 'johndoe1234'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'Username must at least be 5 characters long.')

    def test_view_post_context_long_username(self):
        response = self.client.post(reverse('user_register'),\
                                    {'username': 'johnjohnjohnjohnjohnjohnjohnjohn', 'email': 'admin@example.com',\
                                    'password': 'johndoe1234', 'password_confirm': 'johndoe1234'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'Username cannot be longer than 30 characters.')

    def test_view_post_context_short_password(self):
        response = self.client.post(reverse('user_register'),\
                                    {'username': 'johndoe2', 'email': 'johndoe2@example.com',\
                                    'password': 'johndoe', 'password_confirm': 'johndoe'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password', 'Password must at least be 8 characters long.')

    def test_view_post_username_exists(self):
        response = self.client.post(reverse('user_register'),\
                                    {'username': 'johndoe', 'email': 'johndoe2@example.com',\
                                    'password': 'johndoe1234', 'password_confirm': 'johndoe1234'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'This username already exists')

    def test_view_post_email_exists(self):
        response = self.client.post(reverse('user_register'),\
                                    {'username': 'johndoe2', 'email': 'johndoe@example.com',\
                                    'password': 'johndoe1234', 'password_confirm': 'johndoe1234'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'This email is already taken')

    def test_view_post_passwords_no_match(self):
        response = self.client.post(reverse('user_register'),\
                                    {'username': 'johndoe2', 'email': 'johndoe2@example.com',\
                                    'password': 'johndoe1234', 'password_confirm': 'johndoe123'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password_confirm', 'Passwords do not match')

    def test_view_post_valid_data(self):
        response = self.client.post(reverse('user_register'),\
                                    {'username': 'johndoe2', 'email': 'johndoe2@example.com',\
                                    'password': 'johndoe1234', 'password_confirm': 'johndoe1234'})
        self.assertTemplateUsed(response, 'forums/templates/message.html')

class ConfirmViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        FossCategory.objects.create(name='TestCategory')
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        Profile.objects.create(user = user, confirmation_code = '12345678')

    def test_view_url_at_desired_location(self):
        response = self.client.get('/accounts/confirm/12345678/johndoe/')
        self.assertRedirects(response, reverse('profile'))

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('confirm', args=('12345678', 'johndoe', )))
        self.assertRedirects(response, reverse('profile'))

    def test_view_if_incorrect_confirmation_code(self):
        response = self.client.get(reverse('confirm', args=('123456789', 'johndoe', )))
        self.assertRedirects(response, reverse('website:home'))

    def test_view_if_incorrect_username(self):
        response = self.client.get(reverse('confirm', args=('123456789', 'johndoe2', )))
        self.assertRedirects(response, reverse('website:home'))

class AccountProfileViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        Profile.objects.create(user = user, confirmation_code = '12345678')

    def test_view_if_not_logged_in(self):
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('profile'))
        self.assertTemplateUsed(response, 'forums/templates/profile.html')

    def test_view_get_context_form(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('profile'))
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], ProfileForm)

    def test_view_post_no_first_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.post(reverse('profile'),\
                                    {'last_name': 'Doe', 'phone': '+6590500092',\
                                    'address': 'TestAddress'})
        self.assertFormError(response, 'form', 'first_name', 'First name field required')

    def test_view_post_no_last_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.post(reverse('profile'),\
                                    {'first_name': 'John', 'phone': '+6590500092',\
                                    'address': 'TestAddress'})
        self.assertFormError(response, 'form', 'last_name', 'Last name field required')

    def test_view_post_invalid_phone(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.post(reverse('profile'),\
                                    {'first_name': 'John', 'last_name': 'Doe',\
                                    'phone': '9050abcd', 'address': 'TestAddress'})
        self.assertFormError(response, 'form', 'phone', 'Invalid phone number format')

    def test_view_post_short_phone(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.post(reverse('profile'),\
                                    {'first_name': 'John', 'last_name': 'Doe',\
                                    'phone': '9050', 'address': 'TestAddress'})
        self.assertFormError(response, 'form', 'phone', 'Phone number cannot be shorter than 8 characters')
    
    def test_view_post_long_phone(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.post(reverse('profile'),\
                                    {'first_name': 'John', 'last_name': 'Doe',\
                                    'phone': '12341234123412341', 'address': 'TestAddress'})
        self.assertFormError(response, 'form', 'phone', 'Phone number cannot be longer than 16 characters')

    def test_view_post_nonalphanumeric_first_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.post(reverse('profile'),\
                                    {'first_name': 'John1234@#', 'last_name': 'Doe',\
                                    'phone': '12345678', 'address': 'TestAddress'})
        self.assertFormError(response, 'form', 'first_name', 'Only alphanumeric')

    def test_view_post_nonalphanumeric_last_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.post(reverse('profile'),\
                                    {'first_name': 'John', 'last_name': 'Doe1234@#',\
                                    'phone': '12345678', 'address': 'TestAddress'})
        self.assertFormError(response, 'form', 'last_name', 'Only alphanumeric')

    def test_view_post_invalid_data(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.post(reverse('profile'),\
                                    {'first_name': 'John', 'last_name': 'Doe',\
                                    'phone': '9050abcd', 'address': 'TestAddress'})
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], ProfileForm)
        self.assertTemplateUsed(response, 'forums/templates/profile.html')

    def test_view_post_valid_data_updated(self):
        self.client.login(username='johndoe', password='johndoe')
        self.client.post(reverse('profile'),\
                                    {'first_name': 'John', 'last_name': 'Doe',\
                                    'phone': '12345678', 'address': 'TestAddress'})
        user = User.objects.get(username='johndoe')
        profile = Profile.objects.get(user=user)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(profile.phone, '12345678')
        self.assertEqual(profile.address, 'TestAddress')

    def test_view_post_valid_data_redirect(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.post(reverse('profile'),\
                                    {'first_name': 'John', 'last_name': 'Doe',\
                                    'phone': '12345678', 'address': 'TestAddress'})
        user_id = User.objects.get(username='johndoe').id
        self.assertRedirects(response, reverse('view_profile', args=(user_id, )))

class AccountViewProfileViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        User.objects.create_user('johndoe2', 'johndoe2@example.com', 'johndoe2')
        Profile.objects.create(user = user, confirmation_code = '12345678')
        category = FossCategory.objects.create(name='TestCategory', email='category@example.com')
        question = Question.objects.create(user=user, category=category, title='TestQuestion')
        Answer.objects.create(question=question, uid=user.id, body='TestAnswer')

    def test_view_if_not_logged_in(self):
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('view_profile', args=(user_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get('/accounts/view-profile/{0}/'.format(user_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('view_profile', args=(user_id, )))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('view_profile', args=(user_id, )))
        self.assertTemplateUsed(response, 'forums/templates/view-profile.html')

    def test_view_context_flag_different_user(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('view_profile', args=(user_id, )))
        self.assertTrue('show' in response.context)
        self.assertFalse(response.context['show'])

    def test_view_context_flag_same_user(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('view_profile', args=(user_id, )))
        self.assertTrue('show' in response.context)
        self.assertTrue(response.context['show'])

    def test_view_context_profile(self):
        self.client.login(username='johndoe', password='johndoe')
        user = User.objects.get(username='johndoe')
        response = self.client.get(reverse('view_profile', args=(user.id, )))
        profile = Profile.objects.get(user=user)
        self.assertTrue('profile' in response.context)
        self.assertEqual(response.context['profile'], profile)

    def test_view_context_form(self):
        self.client.login(username='johndoe', password='johndoe')
        user = User.objects.get(username='johndoe')
        response = self.client.get(reverse('view_profile', args=(user.id, )))
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], ProfileForm)

    def test_view_context_questions(self):
        self.client.login(username='johndoe', password='johndoe')
        user = User.objects.get(username='johndoe')
        response = self.client.get(reverse('view_profile', args=(user.id, )))
        question_id = Question.objects.get(title='TestQuestion').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],\
                ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

    def test_view_context_answers(self):
        self.client.login(username='johndoe', password='johndoe')
        user = User.objects.get(username='johndoe')
        response = self.client.get(reverse('view_profile', args=(user.id, )))
        self.assertTrue('answers' in response.context)
        self.assertQuerysetEqual(response.context['answers'],\
                ['<Answer: TestCategory - TestQuestion - TestAnswer>'])

class UserLoginViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe', first_name='John', last_name='Doe')
        user = User.objects.create_user('johndoe2', 'johndoe2@example.com', 'johndoe2')
        user.is_active = False
        user.save()

    def test_view_url_at_desired_location(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('user_login'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('user_login'))
        self.assertTemplateUsed(response, 'forums/templates/user-login.html')

    def test_view_redirect_if_logged_in(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('user_login'))
        self.assertRedirects(response, reverse('website:home'))

    def test_view_get_context_form(self):
        response = self.client.get(reverse('user_login'))
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], UserLoginForm)

    def test_view_get_context_next_without_nexturl(self):
        response = self.client.get(reverse('user_login'))
        self.assertTrue('next' in response.context)
        self.assertEqual(response.context['next'], None)

    def test_view_get_context_next_with_nexturl(self):
        response = self.client.get(reverse('user_login'), data=dict(next=reverse('website:new_question')))
        self.assertTrue('next' in response.context)
        self.assertEqual(response.context['next'], '/new-question/')

    def test_view_post_no_username(self):
        response = self.client.post(reverse('user_login'),\
            {'username': None, 'password': 'johndoe'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', '__all__', 'Invalid username or password')

    def test_view_post_no_password(self):
        response = self.client.post(reverse('user_login'),\
            {'username': 'johndoe', 'password': None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', '__all__', 'Invalid username or password')

    def test_view_post_wrong_username(self):
        response = self.client.post(reverse('user_login'),\
            {'username': 'johndoe1', 'password': 'johndoe'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', '__all__', 'Invalid username or password')

    def test_view_post_wrong_password(self):
        response = self.client.post(reverse('user_login'),\
            {'username': 'johndoe', 'password': 'johndoe1'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', '__all__', 'Invalid username or password')

    def test_view_post_blocked_user(self):
        response = self.client.post(reverse('user_login'),\
            {'username': 'johndoe2', 'password': 'johndoe2'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', '__all__', 'Invalid username or password')

    def test_view_post_invalid_uses_correct_template(self):
        response = self.client.post(reverse('user_login'),\
            {'username': 'johndoe2', 'password': 'johndoe'})
        self.assertTemplateUsed(response, 'forums/templates/user-login.html')

    def test_view_post_invalid_context_form(self):
        response = self.client.post(reverse('user_login'),\
            {'username': 'johndoe2', 'password': 'johndoe'})
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], UserLoginForm)

    def test_view_post_invalid_context_next_without_nexturl(self):
        response = self.client.post(reverse('user_login'),\
            {'username': 'johndoe2', 'password': 'johndoe'})
        self.assertTrue('next' in response.context)
        self.assertEqual(response.context['next'], None)

    def test_view_post_invalid_context_next_with_nexturl(self):
        response = self.client.post(reverse('user_login'),\
            data=dict({'username': 'johndoe2', 'password': 'johndoe'}, next=reverse('website:new_question')))
        self.assertTrue('next' in response.context)
        self.assertEqual(response.context['next'], '/new-question/')

    def test_view_post_valid_without_nexturl(self):
        response = self.client.post(reverse('user_login'),\
            {'username': 'johndoe', 'password': 'johndoe'})
        self.assertRedirects(response, reverse('website:home'))

    def test_view_post_valid_with_nexturl(self):
        response = self.client.post(reverse('user_login'),\
            data=dict({'username': 'johndoe', 'password': 'johndoe'}, next=reverse('website:new_question')))
        self.assertRedirects(response, reverse('website:new_question'))

class UserLogoutViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get('/accounts/logout/')
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('user_logout'))
        self.assertRedirects(response, reverse('website:home'))

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('user_logout'))
        self.assertRedirects(response, reverse('website:home'))
        
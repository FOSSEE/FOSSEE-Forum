from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from website.models import FossCategory, Question
from website.forms import NewQuestionForm, AnswerQuestionForm, AnswerCommentForm
from forums.forms import *


class NewQuestionFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_category_queryset(self):
        form = NewQuestionForm()
        self.assertQuerysetEqual(form.fields['category'].queryset, FossCategory.objects.order_by('name'), transform=lambda x: x)

    def test_category_required(self):
        form = NewQuestionForm()
        self.assertTrue(form.fields['category'].required)

    def test_category_empty_label(self):
        form = NewQuestionForm()
        self.assertEqual(form.fields['category'].empty_label, "Select a Foss category")

    def test_category_error_required(self):
        form = NewQuestionForm()
        self.assertEqual(form.fields['category'].error_messages['required'],\
                            'Select a category')

    def test_title_required(self):
        form = NewQuestionForm()
        self.assertTrue(form.fields['title'].required)

    def test_title_error_required(self):
        form = NewQuestionForm()
        self.assertEqual(form.fields['title'].error_messages['required'],\
                            'Title field required')

    def test_body_required(self):
        form = NewQuestionForm()
        self.assertTrue(form.fields['body'].required)

    def test_body_error_required(self):
        form = NewQuestionForm()
        self.assertEqual(form.fields['body'].error_messages['required'],\
                            'Question field required')

    def test_is_spam_required(self):
        form = NewQuestionForm()
        self.assertFalse(form.fields['is_spam'].required)

    def test_image_help_text(self):
        form = NewQuestionForm()
        self.assertEqual(form.fields['image'].help_text, "Upload image")

    def test_image_required(self):
        form = NewQuestionForm()
        self.assertFalse(form.fields['image'].required)

    def test_too_short_title(self):
        category = FossCategory.objects.get(name = "TestCategory")
        title = 'ShortTitle'
        form = NewQuestionForm(data = {'category': category.id, 'title': title, 'body': 'Test question body', 'tutorial': 'TestTutorial'})
        self.assertFalse(form.is_valid())
    
    def test_title_is_space(self):
        category = FossCategory.objects.get(name = "TestCategory")
        title = '              '
        form = NewQuestionForm(data = {'category': category.id, 'title': title, 'body': 'Test question body', 'tutorial': 'TestTutorial'})
        self.assertFalse(form.is_valid())

    def test_title_is_only_tags(self):
        category = FossCategory.objects.get(name = "TestCategory")
        title = '<p><p><div><div>'
        form = NewQuestionForm(data = {'category': category.id, 'title': title, 'body': 'Test question body', 'tutorial': 'TestTutorial'})
        self.assertFalse(form.is_valid())

    def test_title_exists(self):
        category = FossCategory.objects.get(name = "TestCategory")
        question = Question.objects.get(title = "TestQuestion")
        title = question.title
        form = NewQuestionForm(data = {'category': category.id, 'title': title, 'body': 'Test question body', 'tutorial': 'TestTutorial'})
        self.assertFalse(form.is_valid())

    def test_too_short_body(self):
        category = FossCategory.objects.get(name = "TestCategory")
        body = 'ShortBody'
        form = NewQuestionForm(data = {'category': category.id, 'title': 'Test question title', 'body': body, 'tutorial': 'TestTutorial'})
        self.assertFalse(form.is_valid())

    def test_body_is_space(self):
        category = FossCategory.objects.get(name = "TestCategory")
        body = '         '
        form = NewQuestionForm(data = {'category': category.id, 'title': 'Test question title', 'body': body, 'tutorial': 'TestTutorial'})
        self.assertFalse(form.is_valid())
    
    def test_body_is_only_tags(self):
        category = FossCategory.objects.get(name = "TestCategory")
        body = '<p><p><div><div>'
        form = NewQuestionForm(data = {'category': category.id, 'title': 'Test question title', 'body': body, 'tutorial': 'TestTutorial'})
        self.assertFalse(form.is_valid())

    def test_valid_data_entered(self):
        category = FossCategory.objects.get(name = "TestCategory")
        body = 'Test question body'
        title = 'Test question title'
        form = NewQuestionForm(data = {'category': category.id, 'title': title, 'body': body, 'tutorial': 'TestTutorial'})
        self.assertTrue(form.is_valid())

class AnswerQuestionFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Setup sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_body_required(self):
        form = AnswerQuestionForm()
        self.assertTrue(form.fields['body'].required)

    def test_body_error_required(self):
        form = AnswerQuestionForm()
        self.assertEqual(form.fields['body'].error_messages['required'],\
                            'Answer field required')

    def test_image_help_text(self):
        form = AnswerQuestionForm()
        self.assertEqual(form.fields['image'].help_text, "Upload image")

    def test_image_required(self):
        form = AnswerQuestionForm()
        self.assertFalse(form.fields['image'].required)

    def test_too_short_body(self):
        question = Question.objects.get(title = "TestQuestion")
        body = 'ShortBody'
        form = AnswerQuestionForm(data = {'question': question.id, 'body': body})
        self.assertFalse(form.is_valid())

    def test_body_is_space(self):
        question = Question.objects.get(title = "TestQuestion")
        body = '         '
        form = AnswerQuestionForm(data = {'question': question.id, 'body': body})
        self.assertFalse(form.is_valid())

    def test_body_is_only_tags(self):
        question = Question.objects.get(title = "TestQuestion")
        body = '<p><div><p><div>    '
        form = AnswerQuestionForm(data = {'question': question.id, 'body': body})
        self.assertFalse(form.is_valid())

    def test_valid_data_entered(self):
        question = Question.objects.get(title = "TestQuestion")
        body = 'Test answer body'
        form = AnswerQuestionForm(data = {'question': question.id, 'body': body})
        self.assertTrue(form.is_valid())

class AnswerCommentFormTest(TestCase):

    def test_body_required(self):
        form = AnswerCommentForm()
        self.assertTrue(form.fields['body'].required)

    def test_body_error_required(self):
        form = AnswerCommentForm()
        self.assertEqual(form.fields['body'].error_messages['required'],\
                            'Comment field required')

    def test_body_is_space(self):
        body = '         '
        form = AnswerCommentForm(data = {'body': body})
        self.assertFalse(form.is_valid())

    def test_body_is_only_tags(self):
        body = '<p><div><p><div> '
        form = AnswerCommentForm(data = {'body': body})
        self.assertFalse(form.is_valid())

    def test_valid_data_entered(self):
        body = 'Test comment body'
        form = AnswerCommentForm(data = {'body': body})
        self.assertTrue(form.is_valid())

class UserLoginFormTest(TestCase):

    @classmethod
    def setUp(cls):
        """Set up sample user"""
        User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")

    def test_username_is_none(self):
        form = UserLoginForm(data = {'username': None, 'password': 'jonhdoe'})
        self.assertFalse(form.is_valid())

    def test_password_is_none(self):
        form = UserLoginForm(data = {'username': 'johndoe', 'password': None})
        self.assertFalse(form.is_valid())

    def test_wrong_username(self):
        form = UserLoginForm(data = {'username': 'testuser', 'password': 'johndoe'})
        self.assertFalse(form.is_valid())

    def test_wrong_password(self):
        form = UserLoginForm(data = {'username': 'johndoe', 'password': 'testuser'})
        self.assertFalse(form.is_valid())

    def test_blocked_user(self):
        user = User.objects.get(username="johndoe")
        user.is_active = False
        user.save()
        form = UserLoginForm(data = {'username': 'johndoe', 'password': 'johndoe'})
        self.assertFalse(form.is_valid())

    def test_valid_credentials(self):
        form = UserLoginForm(data = {'username': 'johndoe', 'password': 'johndoe'})
        self.assertTrue(form.is_valid())

class ProfileFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')

    def test_first_name_required(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user)
        self.assertTrue(form.fields['first_name'].required)

    def test_last_name_required(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user)
        self.assertTrue(form.fields['last_name'].required)

    def test_address_required(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user)
        self.assertFalse(form.fields['address'].required)

    def test_phone_required(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user)
        self.assertFalse(form.fields['phone'].required)

    def test_first_name_error_message(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user)
        self.assertEqual(form.fields['first_name'].error_messages['required'],\
                            'First name field required')

    def test_last_name_error_message(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user)
        self.assertEqual(form.fields['last_name'].error_messages['required'],\
                            'Last name field required')

    def test_invalid_first_name(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user, data = {'first_name': 'john2@#',\
                                            'last_name': 'doe', 'address':'TestAddress'})
        self.assertFalse(form.is_valid())

    def test_invalid_last_name(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user, data = {'first_name': 'john',\
                                            'last_name': 'doe2@#'})
        self.assertFalse(form.is_valid())

    def test_too_long_phone(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user, data = {'first_name': 'john',\
                                            'last_name': 'doe', 'phone':'+352353824938292858',\
                                            'address':'TestAddress'})
        self.assertFalse(form.is_valid())
    
    def test_too_short_phone(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user, data = {'first_name': 'john',\
                                            'last_name': 'doe', 'phone':'+352',\
                                            'address':'TestAddress'})
        self.assertFalse(form.is_valid())

    def test_alphanumeric_phone(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user, data = {'first_name': 'john',\
                                            'last_name': 'doe2', 'phone': '+91acafs349',\
                                            'address':'TestAddress'})
        self.assertFalse(form.is_valid())

    def test_valid_credentials(self):
        user = User.objects.get(username = 'johndoe')
        form = ProfileForm(user = user, data = {'first_name': 'john',\
                                    'last_name': 'doe', 'phone': '+9112345678',\
                                    'address':'TestAddress'})
        self.assertTrue(form.is_valid())

class RegisterFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user('johndoe', 'johndoe@johndoe.com', 'johndoe')

    def test_username_label(self):
        form = RegisterForm()
        self.assertEqual(form.fields['username'].label, _("Username"))

    def test_username_required(self):
        form = RegisterForm()
        self.assertTrue(form.fields['username'].required)

    def test_password_label(self):
        form = RegisterForm()
        self.assertEqual(form.fields['password'].label, _("Password"))

    def test_password_confirm_label(self):
        form = RegisterForm()
        self.assertEqual(form.fields['password_confirm'].label, _("Password (again)"))

    def test_email_label(self):
        form = RegisterForm()
        self.assertEqual(form.fields['email'].label, _("Email"))

    def test_email_required(self):
        form = RegisterForm()
        self.assertTrue(form.fields['email'].required)

    def test_invalid_username(self):
        form_data = {'username': 'johndoe#', 'password': 'johndoe1234',\
                        'password_confirm': 'johndoe1234', 'email': 'johndoe@example.com'}
        form = RegisterForm(data = form_data)
        self.assertFalse(form.is_valid())

    def test_too_short_username(self):
        form_data = {'username': 'john', 'password': 'johndoe1234',\
                        'password_confirm': 'johndoe1234', 'email': 'johndoe@example.com'}
        form = RegisterForm(data = form_data)
        self.assertFalse(form.is_valid())

    def test_too_long_username(self):
        form_data = {'username': 'johndoejohndoejohndoejohndoejohndoe', 'password': 'johndoe1234',\
                        'password_confirm': 'johndoe1234', 'email': 'johndoe@example.com'}
        form = RegisterForm(data = form_data)
        self.assertFalse(form.is_valid())

    def test_too_short_password(self):
        form_data = {'username': 'johndoejohndoe', 'password': 'johndoe',\
                        'password_confirm': 'johndoe', 'email': 'johndoe@example.com'}
        form = RegisterForm(data = form_data)
        self.assertFalse(form.is_valid())

    def test_existing_username(self):
        form_data = {'username': 'johndoe', 'password': 'johndoe1234',\
                        'password_confirm': 'johndoe1234', 'email': 'johndoe@example.com'}
        form = RegisterForm(data = form_data)
        self.assertFalse(form.is_valid())

    def test_existing_email(self):
        form_data = {'username': 'johndoejohndoe', 'password': 'johndoe1234',\
                        'password_confirm': 'johndoe1234', 'email': 'johndoe@johndoe.com'}
        form = RegisterForm(data = form_data)
        self.assertFalse(form.is_valid())

    def test_different_passwords(self):
        form_data = {'username': 'johndoejohndoe', 'password': 'johndoe1234',\
                        'password_confirm': 'johndoe12345', 'email': 'johndoe@example.com'}
        form = RegisterForm(data = form_data)
        self.assertFalse(form.is_valid())

    def test_valid_credentials(self):
        form_data = {'username': 'johndoejohndoe', 'password': 'johndoe1234',\
                        'password_confirm': 'johndoe1234', 'email': 'johndoe@example.com'}
        form = RegisterForm(data = form_data)
        self.assertTrue(form.is_valid())
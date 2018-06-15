from django.test import TestCase
from django.contrib.auth.models import User
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

    def test_valid_data_entered(self):
        body = 'Test comment body'
        form = AnswerCommentForm(data = {'body': body})
        self.assertTrue(form.is_valid())

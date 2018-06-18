from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from website.models import *
from website.views import is_moderator

class HomeViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")
        Question.objects.create(user=user, category=category, title="TestQuestion 2", is_spam=True)

    def test_view_url_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('website:home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('website:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/index.html')

    def test_view_context_questions(self):
        response = self.client.get(reverse('website:home'))
        question_id = Question.objects.get(title="TestQuestion").id
        self.assertEqual(response.status_code, 200)
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                    ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

    def test_view_context_categories(self):
        response = self.client.get(reverse('website:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'],
                                    ['<FossCategory: TestCategory>'])

class QuestionsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")
        Question.objects.create(user=user, category=category, title="TestQuestion 2", is_spam=True)

    def test_view_url_at_desired_location(self):
        response = self.client.get('/questions/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('website:questions'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('website:questions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/questions.html')

    def test_view_context_questions(self):
        response = self.client.get(reverse('website:home'))
        question_id = Question.objects.get(title="TestQuestion").id
        self.assertEqual(response.status_code, 200)
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                    ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

class GetQuestionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        answer = Answer.objects.create(question=question, uid=user.id)
        AnswerComment.objects.create(answer=answer, uid=user.id, body="TestAnswerComment")

    def test_view_url_at_desired_location(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get('/question/{0}/'.format(question_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-question.html')
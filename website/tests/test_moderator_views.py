from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.conf import settings
from website.models import *
from website.forms import *


class AnswerDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        group = Group.objects.create(name="TestCategory_moderator")
        ModeratorGroup.objects.create(group=group, category=category)
        user.groups.add(group)
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        Answer.objects.create(question=question, uid=user.id, body="TestAnswer")

    def test_view_redirect_if_not_logged_in(self):
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_delete', args=(answer_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_delete', args=(answer_id, )), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.get('/answer_delete/{0}/'.format(answer.id))
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.get(reverse('website:answer_delete', args=(answer.id, )))
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_delete_answer(self):
        self.client.login(username='johndoe', password='johndoe')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.get(reverse('website:answer_delete', args=(answer.id, )))
        try:
            Answer.objects.get(body='TestAnswer')
            self.fail('Answer not deleted.')
        except:
            self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

class MarkAnswerSpamViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        group = Group.objects.create(name="TestCategory_moderator")
        ModeratorGroup.objects.create(group=group, category=category)
        user.groups.add(group)
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        Answer.objects.create(question=question, uid=user.id, body="TestAnswer")

    def test_view_redirect_if_not_logged_in(self):
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_delete', args=(answer_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_delete', args=(answer_id, )), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.get('/mark_answer_spam/{0}/'.format(answer.id))
        self.assertRedirects(response, '/question/{0}/#answer{1}/'.format(question_id, answer.id))

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.get(reverse('website:mark_answer_spam', args=(answer.id, )))
        self.assertRedirects(response, '/question/{0}/#answer{1}/'.format(question_id, answer.id))

    def test_view_post_answer_spam(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswer').id
        self.client.post(reverse('website:mark_answer_spam', args=(answer_id, )),\
                                        {'selector': 'spam'})
        answer = Answer.objects.get(id=answer_id)
        self.assertTrue(answer.is_spam)

    def test_view_post_answer_non_spam(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswer').id
        self.client.post(reverse('website:mark_answer_spam', args=(answer_id, )),\
                                        {'selector': 'non-spam'})
        answer = Answer.objects.get(id=answer_id)
        self.assertFalse(answer.is_spam)

class ModeratorHomeViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        group = Group.objects.create(name="TestCategory_moderator")
        ModeratorGroup.objects.create(group=group, category=category)
        user.groups.add(group)
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:moderator_home'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get(reverse('website:moderator_home'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get('/moderator/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTemplateUsed(response, 'website/templates/moderator/index.html')

    def test_view_context_questions(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_home'))
        question_id = Question.objects.get(title='TestQuestion').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],\
                                    ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

    def test_view_context_categories(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'],\
                                    ['<FossCategory: TestCategory>'])

class ModeratorQuestionsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        group = Group.objects.create(name="TestCategory_moderator")
        ModeratorGroup.objects.create(group=group, category=category)
        user.groups.add(group)
        Question.objects.create(user=user, category=category, title="TestQuestion")
        Question.objects.create(user=user, category=category, title="TestQuestion2", is_spam=True)

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:moderator_questions'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get(reverse('website:moderator_questions'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get('/moderator/questions/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_questions'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_questions'))
        self.assertTemplateUsed(response, 'website/templates/moderator/questions.html')

    def test_view_context_questions(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_questions'))
        question_id = Question.objects.get(title='TestQuestion').id
        question2_id = Question.objects.get(title='TestQuestion2').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],\
                                    ['<Question: {0} - TestCategory -  - TestQuestion2 - johndoe>'.format(question2_id),\
                                    '<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

    def test_view_context_spam_questions(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get('/moderator/questions/?spam')
        question2_id = Question.objects.get(title='TestQuestion2').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],\
                                    ['<Question: {0} - TestCategory -  - TestQuestion2 - johndoe>'.format(question2_id)])

    def test_view_context_non_spam_questions(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get('/moderator/questions/?non-spam')
        question_id = Question.objects.get(title='TestQuestion').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],\
                                    ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

class ModeratorUnansweredViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        group = Group.objects.create(name="TestCategory_moderator")
        ModeratorGroup.objects.create(group=group, category=category)
        user.groups.add(group)
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get(reverse('website:moderator_unanswered'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get('/moderator/unanswered/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertTemplateUsed(response, 'website/templates/moderator/unanswered.html')

    def test_view_context_questions(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_unanswered'))
        question_id = Question.objects.get(title='TestQuestion').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],\
                                    ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])
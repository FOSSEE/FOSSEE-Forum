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
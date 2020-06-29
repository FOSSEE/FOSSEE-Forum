from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.conf import settings
from website.models import *
from website.forms import *


class ModeratorActivateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a user
        User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Category
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)

    def test_view_redirect_if_not_logged_in(self):
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_activate'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_activate'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Accessing the Page
        response = self.client.get('/moderator/activate/', follow=True)
        self.assertTrue(self.client.session['MODERATOR_ACTIVATED'])
        self.assertRedirects(response, reverse('website:moderator_home'))

    def test_view_url_accessible_by_name(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_activate'), follow=True)
        self.assertTrue(self.client.session['MODERATOR_ACTIVATED'])
        self.assertRedirects(response, reverse('website:moderator_home'))

    def test_view_resolves_next(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_activate'),
                                   {'next': '/questions/'}, follow=True)
        self.assertTrue(self.client.session['MODERATOR_ACTIVATED'])
        self.assertRedirects(response, reverse('website:moderator_questions'))

class ModeratorDeactivateViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Create a user
        User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Category
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:moderator_activate'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_activate'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get('/moderator/deactivate/', follow=True)
        self.assertFalse(self.client.session['MODERATOR_ACTIVATED'])
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_accessible_by_name(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_deactivate'), follow=True)
        self.assertFalse(self.client.session['MODERATOR_ACTIVATED'])
        self.assertRedirects(response, reverse('website:home'))

    def test_view_resolves_next(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_deactivate'),
                                   {'next': '/moderator/questions/'}, follow=True)
        self.assertFalse(self.client.session['MODERATOR_ACTIVATED'])
        self.assertRedirects(response, reverse('website:questions'))

class ModeratorHomeViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Super Moderator
        super_mod = User.objects.create_user('super_mod', 'super_mod@example.com', 'super_mod')
        group = Group.objects.create(name="forum_moderator")
        super_mod.groups.add(group)
        # Create Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample questions
        Question.objects.create(user=user, category=category1, title="TestQuestion1")
        Question.objects.create(user=user, category=category2, title="TestQuestion2")

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:moderator_home'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:moderator_home'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_redirect_if_not_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get('/moderator/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTemplateUsed(response, 'website/templates/moderator/index.html')

    def test_view_context_questions_super_moderator(self):
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('questions' in response.context)
        # Questions of all categories must be present
        self.assertEqual(len(response.context['questions']), 2)

    def test_view_context_questions_super_moderator_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('questions' in response.context)
        # Questions of all categories must be present
        self.assertEqual(len(response.context['questions']), 1)

    def test_view_context_questions(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        question_id = Question.objects.get(title='TestQuestion1').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                 ['<Question: {0} - TestCategory1 -  - TestQuestion1 - johndoe>'.format(question_id)])

    def test_view_context_questions_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'], [])

    def test_view_context_categories_super_moderator(self):
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        # All categories must be present
        self.assertEqual(len(response.context['categories']), 2)

    def test_view_context_categories_super_moderator_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        # All categories must be present
        self.assertEqual(len(response.context['categories']), 1)

    def test_view_context_categories(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'], ['<FossCategory: TestCategory1>'])

    def test_view_context_categories_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'], [])

class ModeratorQuestionsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Super Moderator
        super_mod = User.objects.create_user('super_mod', 'super_mod@example.com', 'super_mod')
        group = Group.objects.create(name="forum_moderator")
        super_mod.groups.add(group)
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample questions
        Question.objects.create(user=user, category=category1, title="TestQuestion1")
        Question.objects.create(user=user, category=category1, title="TestQuestion2", is_spam=True)
        Question.objects.create(user=user, category=category2, title="TestQuestion3")

    def test_view_redirect_if_not_logged_in(self):
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_questions'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        # Log in the user
        self.client.login(username='johndoe', password='johndoe')
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_questions'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_redirect_if_not_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_questions'), follow=True)
        self.assertRedirects(response, reverse('website:questions'))

    def test_view_url_at_desired_location(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get('/moderator/questions/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_questions'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_questions'))
        self.assertTemplateUsed(response, 'website/templates/moderator/questions.html')

    def test_view_context_questions_super_moderator(self):
        # Log in the Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_questions'))
        self.assertTrue('questions' in response.context)
        # All Questions of all categories must be present
        self.assertEqual(len(response.context['questions']), 3)

    def test_view_context_questions_super_moderator_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_questions'))
        self.assertTrue('questions' in response.context)
        # All Questions of all categories must be present
        self.assertEqual(len(response.context['questions']), 1)

    def test_view_context_questions(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_questions'))
        question1_id = Question.objects.get(title='TestQuestion1').id
        question2_id = Question.objects.get(title='TestQuestion2').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                 ['<Question: {0} - TestCategory1 -  - TestQuestion2 - johndoe>'.format(question2_id),
                                  '<Question: {0} - TestCategory1 -  - TestQuestion1 - johndoe>'.format(question1_id)])

    def test_view_context_questions_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_questions'))
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'], [])

    def test_view_context_spam_questions(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get('/moderator/questions/?spam')
        question2_id = Question.objects.get(title='TestQuestion2').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                    ['<Question: {0} - TestCategory1 -  - TestQuestion2 - johndoe>'.format(question2_id)])

    def test_view_context_non_spam_questions(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get('/moderator/questions/?non-spam')
        question1_id = Question.objects.get(title='TestQuestion1').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                    ['<Question: {0} - TestCategory1 -  - TestQuestion1 - johndoe>'.format(question1_id)])

    def test_view_context_categories_super_moderator(self):
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        # All categories must be present
        self.assertEqual(len(response.context['categories']), 2)

    def test_view_context_categories_super_moderator_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        # All categories must be present
        self.assertEqual(len(response.context['categories']), 1)

    def test_view_context_categories(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'], ['<FossCategory: TestCategory1>'])

    def test_view_context_categories_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'], [])

class ModeratorUnansweredViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Super Moderator
        super_mod = User.objects.create_user('super_mod', 'super_mod@example.com', 'super_mod')
        group = Group.objects.create(name="forum_moderator")
        super_mod.groups.add(group)
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample questions
        Question.objects.create(user=user, category=category1, title="TestQuestion1")
        Question.objects.create(user=user, category=category2, title="TestQuestion2")

    def test_view_redirect_if_not_logged_in(self):
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_redirect_if_not_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get('/moderator/unanswered/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertTemplateUsed(response, 'website/templates/moderator/unanswered.html')

    def test_view_context_questions_super_moderator(self):
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertTrue('questions' in response.context)
        # Questions of all categories must be present
        self.assertEqual(len(response.context['questions']), 2)

    def test_view_context_questions_super_moderator_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertTrue('questions' in response.context)
        # Questions of all categories must be present
        self.assertEqual(len(response.context['questions']), 1)

    def test_view_context_questions(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'))
        question1_id = Question.objects.get(title='TestQuestion1').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                 ['<Question: {0} - TestCategory1 -  - TestQuestion1 - johndoe>'.format(question1_id)])

    def test_view_context_questions_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'], [])

    def test_view_context_categories_super_moderator(self):
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertTrue('categories' in response.context)
        # All categories must be present
        self.assertEqual(len(response.context['categories']), 2)

    def test_view_context_categories_super_moderator_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Super Moderator
        self.client.login(username='super_mod', password='super_mod')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_unanswered'))
        self.assertTrue('categories' in response.context)
        # All categories must be present
        self.assertEqual(len(response.context['categories']), 1)

    def test_view_context_categories(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'], ['<FossCategory: TestCategory1>'])

    def test_view_context_categories_hidden_category(self):
        # Hide 'category1'
        cat1 = FossCategory.objects.get(name='TestCategory1')
        cat1.hidden = True
        cat1.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:moderator_home'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'], [])

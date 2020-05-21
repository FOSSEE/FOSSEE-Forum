from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.conf import settings
from website.models import *
from website.forms import *

class HomeViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Category
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample Questions
        Question.objects.create(user=user, category=category1, title="TestQuestion1")
        Question.objects.create(user=user, category=category1, title="TestQuestion2", is_spam=True)

    def test_view_url_at_desired_location(self):
        # Accessing the Page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        # Accessing the Page
        response = self.client.get(reverse('website:home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        # Accessing the Page
        response = self.client.get(reverse('website:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/index.html')

    def test_view_redirects_if_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:moderator_home'))

    def test_view_context_questions(self):
        # Accessing the Page
        response = self.client.get(reverse('website:home'))
        question_id = Question.objects.get(title="TestQuestion1").id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                    ['<Question: {0} - TestCategory1 -  - TestQuestion1 - johndoe>'.format(question_id)])

    def test_view_context_categories(self):
        # Accessing the Page
        response = self.client.get(reverse('website:home'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'],
                                    ['<FossCategory: TestCategory1>'])

class QuestionsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Category
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample Questions
        Question.objects.create(user=user, category=category1, title="TestQuestion1")
        Question.objects.create(user=user, category=category1, title="TestQuestion2", is_spam=True)

    def test_view_url_at_desired_location(self):
        # Accessing the Page
        response = self.client.get('/questions/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        # Accessing the Page
        response = self.client.get(reverse('website:questions'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        # Accessing the Page
        response = self.client.get(reverse('website:questions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/questions.html')

    def test_view_redirects_if_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Accessing the Page
        response = self.client.get(reverse('website:questions'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:moderator_questions'))

    def test_view_context_questions(self):
        # Accessing the Page
        response = self.client.get(reverse('website:questions'))
        question_id = Question.objects.get(title="TestQuestion1").id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                    ['<Question: {0} - TestCategory1 -  - TestQuestion1 - johndoe>'.format(question_id)])
    
    def test_view_context_categories(self):
        # Accessing the Page
        response = self.client.get(reverse('website:questions'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'],
                                    ['<FossCategory: TestCategory1>'])

class GetQuestionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create a Moderator for 'category2'
        mod2 = User.objects.create_user('mod2', 'mod2@example.com', 'mod2')
        group2 = Group.objects.create(name="TestCategory2 Group")
        moderator_group2 = ModeratorGroup.objects.create(group=group2, category=category2)
        mod2.groups.add(group2)
        # Add some sample Questions, Answers and Comments
        question1 = Question.objects.create(user=user, category=category1, title="TestQuestion1",
                                            sub_category="TestSubCategory", num_votes=1)
        question2 = Question.objects.create(user=user, category=category2, title="TestQuestion2",
                                            is_active=False)
        question3 = Question.objects.create(user=user, category=category2, title="TestQuestion3",
                                            is_spam=True)
        answer = Answer.objects.create(question=question1, uid=user.id, body="TestAnswer")
        Answer.objects.create(question=question1, uid=user.id, body="TestAnswer2", is_active=False)
        AnswerComment.objects.create(answer=answer, uid=user.id, body="TestAnswerComment")

    def test_view_url_at_desired_location(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get('/question/{0}/'.format(question_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTemplateUsed(response, 'website/templates/get-question.html')

    def test_view_uses_correct_template_for_same_category_moderator(self):
        # Log in the 'category1' Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Access a 'category1' question
        question_id = Question.objects.get(title="TestQuestion1").id
        # Access the Page
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-question.html')

    def test_view_uses_correct_template_for_other_category_moderator(self):
        # Log in the 'category2' Moderator
        self.client.login(username='mod2', password='mod2')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        # Access a 'category1' question
        question_id = Question.objects.get(title="TestQuestion1").id
        # Access the Page
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_raise_404_while_accessing_deleted_question(self):
        # Deleted question
        question = Question.objects.get(title="TestQuestion2")
        # Access the Page
        response = self.client.get(reverse('website:get_question', args=(question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_view_raise_404_while_accessing_spam_question(self):
        # Spam question
        question = Question.objects.get(title="TestQuestion3")
        # Access the Page
        response = self.client.get(reverse('website:get_question', args=(question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_view_let_author_access_spam_question(self):
        # Log in the author
        login = self.client.login(username='johndoe', password='johndoe')
        # Spam question
        question = Question.objects.get(title="TestQuestion3")
        # Access the Page
        response = self.client.get(reverse('website:get_question', args=(question.id,)))
        self.assertEqual(response.status_code, 200)

    def test_view_context_question(self):
        question = Question.objects.get(title="TestQuestion1")
        response = self.client.get(reverse('website:get_question', args=(question.id,)))
        self.assertTrue('question' in response.context)
        self.assertEqual(response.context['question'], question)

    def test_view_context_ans_count(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('ans_count' in response.context)
        self.assertEqual(response.context['ans_count'], 1)

    def test_view_context_ans_count_moderator_activated(self):
        # Log in the question category Moderator
        login = self.client.login(username='mod1', password='mod1')
        # Activate Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('ans_count' in response.context)
        self.assertEqual(response.context['ans_count'], 2)

    def test_view_context_sub_category(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('sub_category' in response.context)
        self.assertEqual(response.context['sub_category'], True)

    def test_view_context_main_list(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        answer = Answer.objects.get(body = "TestAnswer")
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('main_list' in response.context)
        self.assertEqual(response.context['main_list'], [(answer, [0,0,0])])

    def test_view_context_main_list_moderator_activated(self):
        # Log in the question category Moderator
        login = self.client.login(username='mod1', password='mod1')
        # Activate Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title='TestQuestion1').id
        answer = Answer.objects.get(body = 'TestAnswer')
        answer2 = Answer.objects.get(body = 'TestAnswer2')
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('main_list' in response.context)
        self.assertEqual(response.context['main_list'], [(answer, [0,0,0]), (answer2, [0,0,0])])

    def test_view_context_form(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], AnswerQuestionForm)

    def test_view_context_thisUserUpvote(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('thisUserUpvote' in response.context)
        self.assertEqual(response.context['thisUserUpvote'], 0)

    def test_view_context_thisUserDownvote(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('thisUserDownvote' in response.context)
        self.assertEqual(response.context['thisUserDownvote'], 0)

    def test_view_context_net_count(self):
        question_id = Question.objects.get(title="TestQuestion1").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('net_count' in response.context)
        self.assertEqual(response.context['net_count'], 1)

class NewQuestionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        # Create two users
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2", first_name="John", last_name="Doe")
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Sample Question
        Question.objects.create(user=user, category=category1, title="TestQuestion")

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:new_question'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_no_fullname(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:new_question'))
        self.assertRedirects(response, '/accounts/profile/?next=/new-question/')

    def test_view_redirect_if_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        response = self.client.get(reverse('website:new_question'))
        self.assertRedirects(response, '/moderator/')

    def test_view_url_loads_with_correct_template(self):
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get('/new-question/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('website:new_question'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/new-question.html')

    def test_view_post_no_category(self):
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.post(reverse('website:new_question'),
                                    {'title': 'Test question title',
                                     'body': 'Test question body',
                                     'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'category', 'Select a category')

    def test_view_post_no_title(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id,
                                     'body': 'Test question body',
                                     'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title field required')

    def test_view_post_no_body(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id,
                                     'title': 'Test question title',
                                     'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Question field required')

    def test_view_post_title_only_spaces(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'title': '  &nbsp;             ',
                                     'body': 'Test question body', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title cannot be only spaces')

    def test_view_post_title_only_tags(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'title': '<p><div></div></p>',
                                     'body': 'Test question body', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title cannot be only tags')

    def test_view_post_title_too_short(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'title': 'TooShort',
                                     'body': 'Test question body', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title should be longer than 12 characters')

    def test_view_post_title_already_exists(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'title': 'TestQuestion',
                                     'body': 'Test question body', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'This title already exists')

    def test_view_post_body_only_spaces(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'title': 'Test question title',
                                     'body': '           &nbsp;     ', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only spaces')

    def test_view_post_body_only_tags(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'body': '<p><div></div></p>',
                                     'title': 'Test question title', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only tags')

    def test_view_post_body_too_short(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'body': 'TooShort',
                                     'title': 'Test question title', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body should be minimum 12 characters long')

    def test_view_post_spam_question(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'body': 'swiss replica watches buy',
                                     'title': 'Test question title', 'tutorial': 'None'})
        question_id = Question.objects.get(title='Test question title').id
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_post_valid_data(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'body': 'Test question body',
                                     'title': 'Test question title', 'tutorial': 'None'})
        question_id = Question.objects.get(title='Test question title').id
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_get_context(self):
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get(reverse('website:new_question'))
        self.assertTrue('category' in response.context)
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], NewQuestionForm)

    def test_view_post_context_when_form_error(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory1')
        response = self.client.post(reverse('website:new_question'),
                                    {'category': category.id, 'body': 'TooShort',
                                     'title': 'Test question title', 'tutorial': 'None'})
        self.assertTrue('category' in response.context)
        self.assertEqual(int(response.context['category']), category.id)
        self.assertTrue('tutorial' in response.context)
        self.assertEqual(response.context['tutorial'], 'None')
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], NewQuestionForm)

class QuestionAnswerViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2", first_name="John", last_name="Doe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_view_redirect_if_not_logged_in(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:question_answer', args=(question_id,)))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_no_fullname(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:question_answer', args=(question_id,)))
        self.assertRedirects(response, '/accounts/profile/?next=/question-answer/{0}/'.format(question_id))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get('/question-answer/{0}/'.format(question_id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/question/{0}/'.format(question_id))

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:question_answer', args=(question_id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/question/{0}/'.format(question_id))

    def test_view_post_no_answer(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),
                                    {'question': question_id})
        self.assertTrue("Answer field cannot be empty."
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)

    def test_view_post_too_short_body(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),
                                    {'body': 'TooShort', 'question': question_id})
        self.assertTrue("Answer body should be minimum 12 characters long."
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        # self.assertFormError(response, 'form', 'body', 'Body should be minimum 12 characters long')

    def test_view_post_body_only_spaces(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),
                                    {'body': '        &nbsp;          ', 'question': question_id})
        self.assertTrue("Answer body cannot have spaces only."
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)

    def test_view_post_body_only_tags(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),\
                                    {'body': '<p><div></div></p>        ', 'question': question_id})
        self.assertTrue("Answer body cannot have tags only."
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)

    @override_settings(GOOGLE_RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
                       GOOGLE_RECAPTCHA_SITE_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
    def test_view_post_notification_created(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        self.client.post(reverse('website:question_answer', args=(question_id,)),\
                                    {'body': 'Test question body', 'question': question_id})
        try:
            user_id = User.objects.get(username='johndoe').id
            notification = Notification.objects.get(uid=user_id, qid=question_id)
            self.assertIsInstance(notification, Notification)
        except:
            self.fail('Notification object not created.')

    @override_settings(GOOGLE_RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
                       GOOGLE_RECAPTCHA_SITE_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
    def test_view_post_valid_data(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),
                                    {'body': 'Test question body', 'question': question_id})
        self.assertTrue(Answer.objects.filter(body='Test question body').exists())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question_id,)))
    
class AnswerCommentViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        user2 = User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2", first_name="John", last_name="Doe")
        user3 = User.objects.create_user("johndoe3", "johndoe3@example.com", "johndoe3")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        answer = Answer.objects.create(question=question, uid=user.id, body="TestAnswer")
        AnswerComment.objects.create(answer=answer, uid=user3.id, body="TestAnswerComment")

    def test_view_redirect_if_not_logged_in(self):
        answer_id = Answer.objects.get(body="TestAnswer").id
        response = self.client.get(reverse('website:answer_comment', args=(answer_id,)))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_no_fullname(self):
        answer_id = Answer.objects.get(body="TestAnswer").id
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:answer_comment', args=(answer_id,)))
        self.assertRedirects(response, f'/accounts/profile/?next=/answer-comment/{answer_id}/')

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer = Answer.objects.get(body="TestAnswer")
        response = self.client.get('/answer-comment/{0}/'.format(answer.id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/question/{0}/#answer{1}'.format(answer.question.id, answer.id))

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer = Answer.objects.get(body="TestAnswer")
        response = self.client.get(reverse('website:answer_comment', args=(answer.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/question/{0}/#answer{1}'.format(answer.question.id, answer.id))

    def test_view_does_not_load(self):
        answer = Answer.objects.get(body="TestAnswer")
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get(reverse('website:answer_comment', args=(answer.id,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-question.html')

    def test_view_post_body_only_spaces(self):
        answer_id = Answer.objects.get(body="TestAnswer").id
        self.client.login(username='johndoe2', password='johndoe2')
        answer_id = Answer.objects.get(body="TestAnswer").id
        response = self.client.post(reverse('website:answer_comment', args=(answer_id,)),
                                    {'body': '        &nbsp;          ', 'answer_id': answer_id})
        self.assertTrue("Comment body cannot have spaces only."
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)

    def test_view_post_body_only_tags(self):
        answer_id = Answer.objects.get(body="TestAnswer").id
        self.client.login(username='johndoe2', password='johndoe2')
        answer_id = Answer.objects.get(body="TestAnswer").id
        response = self.client.post(reverse('website:answer_comment', args=(answer_id,)),
                                    {'body': '<p><div></div></p>     ', 'answer_id': answer_id})
        self.assertTrue("Comment body cannot have tags only."
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)

    def test_view_post_notification_created_answer_creator(self):
        answer_id = Answer.objects.get(body="TestAnswer").id
        self.client.login(username='johndoe2', password='johndoe2')
        answer = Answer.objects.get(body="TestAnswer")
        self.client.post(reverse('website:answer_comment', args=(answer_id,)),
                         {'body': 'Test Answer comment', 'answer_id': answer.id})
        try:
            user_id = User.objects.get(username='johndoe').id
            notification = Notification.objects.get(uid=user_id, qid=answer.question.id, aid=answer.id)
            self.assertIsInstance(notification, Notification)
        except:
            self.fail('Notification not created for answer creator.')

    def test_view_post_notification_created_comment_creators(self):
        answer_id = Answer.objects.get(body="TestAnswer").id
        self.client.login(username='johndoe2', password='johndoe2')
        answer = Answer.objects.get(body="TestAnswer")
        self.client.post(reverse('website:answer_comment', args=(answer_id,)),
                         {'body': 'Test Answer comment', 'answer_id': answer.id})
        try:
            user_id = User.objects.get(username='johndoe3').id
            notification = Notification.objects.get(uid=user_id, qid=answer.question.id, aid=answer.id)
            self.assertIsInstance(notification, Notification)
        except:
            self.fail('Notification not created for comment creators.')

    def test_view_post_valid_data(self):
        answer_id = Answer.objects.get(body="TestAnswer").id
        self.client.login(username='johndoe2', password='johndoe2')
        answer = Answer.objects.get(body="TestAnswer")
        response = self.client.post(reverse('website:answer_comment', args=(answer_id,)),
                                    {'body': 'Test Answer comment', 'answer_id': answer.id})
        self.assertTrue(AnswerComment.objects.filter(body='Test Answer comment').exists())
        self.assertRedirects(response, reverse('website:get_question', args=(answer.question.id, )))

class EditQuestionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        # Add two users
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe", first_name="John", last_name="Doe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create a sample question
        Question.objects.create(user=user, category=category1, title="TestQuestion")

    def test_view_redirect_if_not_logged_in(self):
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:edit_question', args=(question_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_no_fullname(self):
        question_id = Question.objects.get(title='TestQuestion').id
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get(reverse('website:edit_question', args=(question_id, )))
        self.assertRedirects(response, '/accounts/profile/?next=/question/edit/{0}/'.format(question_id))

    def test_view_url_loads_with_correct_template(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get('/question/edit/{0}/'.format(question_id))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('website:edit_question', args=(question_id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/edit-question.html')

    def test_view_loads_correct_template_when_not_authorized(self):
        self.client.login(username='mod1', password='mod1')
        # Moderator Panel not activated
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:edit_question', args=(question_id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')
    
    def test_view_loads_not_authorized_template_when_answer_exists(self):
        self.client.login(username='johndoe', password='johndoe')
        user = User.objects.get(username='johndoe')
        question = Question.objects.get(title='TestQuestion')
        answer = Answer.objects.create(question=question, uid=user.id, body='TestAnswer')
        response = self.client.get(reverse('website:edit_question', args=(question.id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_post_no_category(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.post(reverse('website:edit_question', args=(question_id, )),
                                    {'title': 'Test question title', 'body': 'Test question body',
                                     'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'category', 'Select a category')

    def test_view_post_no_title(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'body': 'Test question body',
                                     'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title field required')

    def test_view_post_no_body(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'title': 'Test question title',
                                     'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Question field required')

    def test_view_post_title_only_spaces(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'title': '  &nbsp;             ',
                                     'body': 'Test question body', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title cannot be only spaces')

    def test_view_post_title_only_tags(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'title': '<p><div></div></p>',
                                     'body': 'Test question body', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title cannot be only tags')

    def test_view_post_title_too_short(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'title': 'TooShort',
                                     'body': 'Test question body', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title should be longer than 12 characters')

    def test_view_post_body_only_spaces(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'title': 'Test question title',
                                     'body': '           &nbsp;     ', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only spaces')

    def test_view_post_body_only_tags(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'body': '<p><div></div></p>',
                                     'title': 'Test question title', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only tags')

    def test_view_post_body_too_short(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'body': 'TooShort',
                                     'title': 'Test question title', 'tutorial': 'None'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body should be minimum 12 characters long')

    def test_view_post_title_exists_allowed(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'title': 'TestQuestion',
                                     'body': 'Test question body', 'tutorial': 'None'})
        self.assertRedirects(response, reverse('website:get_question', args=(question.id, )))

    def test_view_post_mark_spam(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'title': 'TestQuestion',
                                     'body': 'Test question body', 'tutorial': 'None', 'is_spam': True})
        self.assertRedirects(response, reverse('website:get_question', args=(question.id, )))

    def test_view_post_mark_spam_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'title': 'TestQuestion',
                                     'body': 'Test question body', 'tutorial': 'None', 'is_spam': True})
        self.assertRedirects(response, reverse('website:get_question', args=(question.id, )))
        question = Question.objects.get(id = question.id)
        self.assertTrue(question.is_spam)

    def test_view_get_context(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:edit_question', args=(question_id, )))
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], NewQuestionForm)

    def test_view_post_context_when_form_error(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),
                                    {'category': question.category.id, 'body': 'TooShort',
                                     'title': 'Test question title', 'tutorial': 'None'})
        self.assertTrue('category' in response.context)
        self.assertEqual(int(response.context['category']), question.category.id)
        self.assertTrue('tutorial' in response.context)
        self.assertEqual(response.context['tutorial'], 'None')
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], NewQuestionForm)

    def test_view_post_change_data(self):
        # Log in the Author of Question
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        category = FossCategory.objects.get(name='TestCategory2')
        response = self.client.post(reverse('website:edit_question', args=(question_id, )),
                                    {'category': category.id, 'title': 'Test question title',
                                     'body': 'Test question body changed', 'tutorial': 'TestTutorial',
                                     'is_spam': True})
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))
        question = Question.objects.get(id = question_id)
        self.assertEqual(question.category, category)
        self.assertEqual(question.title, 'Test question title')
        self.assertEqual(question.body, 'Test question body changed')
        self.assertEqual(question.sub_category, 'TestTutorial')
        self.assertTrue(question.is_spam)

class AnswerUpdateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
         # Add two users
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe", first_name="John", last_name="Doe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample question and answer
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        Answer.objects.create(question=question, uid=user.id, body="TestAnswer")

    def test_view_redirect_if_not_logged_in(self):
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.post(reverse('website:answer_update'),
                                    {'answer_id': answer_id, 'answer_body': 'TestAnswerBody'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_get_error_at_desired_location(self):
        self.client.login(username="johndoe", password="johndoe")
        response = self.client.get('/answer-update/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')
    
    def test_view_get_error_accessible_by_name(self):
        self.client.login(username="johndoe", password="johndoe")
        response = self.client.get(reverse('website:answer_update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')

    def test_view_post_answer_no_exists(self):
        self.client.login(username="johndoe", password="johndoe")
        answer_id = Answer.objects.get(body='TestAnswer').id + 1
        response = self.client.post(reverse('website:answer_update'),
                                    {'answer_id': answer_id, 'answer_body': 'TestAnswerBody'})
        self.assertEqual(response.status_code, 404)

    def test_view_post_answer_update_not_authorized(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.post(reverse('website:answer_update'),
                                    {'answer_id': answer_id, 'answer_body': 'TestAnswerBody'})
        self.assertTrue("Failed to Update Answer!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)

    def test_view_post_valid_data(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.post(reverse('website:answer_update'),
                                    {'answer_id': answer_id, 'answer_body': 'TestAnswerBody'})
        self.assertTrue("Answer is Successfully Saved!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        
    def test_view_post_answer_update_with_moderator(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.post(reverse('website:answer_update'),
                                    {'answer_id': answer_id, 'answer_body': 'TestAnswerBody'})
        self.assertTrue("Answer is Successfully Saved!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)

class AnswerCommentUpdateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
         # Add two users
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe", first_name="John", last_name="Doe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample question and answer
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        answer = Answer.objects.create(question=question, uid=user.id, body="TestAnswer")
        AnswerComment.objects.create(answer=answer, uid=user.id, body="TestComment")

    def test_view_redirect_if_not_logged_in(self):
        comment_id = AnswerComment.objects.get(body='TestComment').id
        response = self.client.post(reverse('website:answer_comment_update'),
                                    {'comment_id': comment_id, 'comment_body': 'TestCommentBody'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_get_error_at_desired_location(self):
        self.client.login(username="johndoe", password="johndoe")
        response = self.client.get('/answer-comment-update/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')
    
    def test_view_get_error_accessible_by_name(self):
        self.client.login(username="johndoe", password="johndoe")
        response = self.client.get(reverse('website:answer_comment_update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')

    def test_view_post_comment_no_exists(self):
        self.client.login(username="johndoe", password="johndoe")
        comment_id = AnswerComment.objects.get(body='TestComment').id + 1
        response = self.client.post(reverse('website:answer_comment_update'),
                                    {'comment_id': comment_id, 'comment_body': 'TestCommentBody'})
        self.assertEqual(response.status_code, 404)

    def test_view_post_comment_update_not_authorized(self):
        self.client.login(username='johndoe2', password='johndoe2')
        comment_id = AnswerComment.objects.get(body='TestComment').id
        response = self.client.post(reverse('website:answer_comment_update'),
                                    {'comment_id': comment_id, 'comment_body': 'TestCommentBody'})
        self.assertTrue("Failed to Update Comment!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)

    def test_view_post_valid_data(self):
        self.client.login(username='johndoe', password='johndoe')
        comment_id = AnswerComment.objects.get(body='TestComment').id
        response = self.client.post(reverse('website:answer_comment_update'),
                                    {'comment_id': comment_id, 'comment_body': 'TestCommentBody'})
        self.assertTrue("Comment is Successfully Saved!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        
    def test_view_post_comment_update_with_moderator(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        comment_id = AnswerComment.objects.get(body='TestComment').id
        response = self.client.post(reverse('website:answer_comment_update'),
                                    {'comment_id': comment_id, 'comment_body': 'TestCommentBody'})
        self.assertTrue("Comment is Successfully Saved!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)

class QuestionDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        # Create two users
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        # Create a Question Category
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create a sample question
        Question.objects.create(user=user, category=category1, title="TestQuestion")

    def test_view_redirect_if_not_logged_in(self):
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:question_delete', args=(question_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get('/question/delete/{0}/'.format(question_id))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:question_delete', args=(question_id, )))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.post(reverse('website:question_delete', args=(question_id, )))
        self.assertTemplateUsed(response, 'website/templates/question-delete.html')

    def test_view_raise_404_when_question_not_exists(self):
        self.client.login(username="johndoe", password="johndoe")
        question_id = Question.objects.get(title='TestQuestion').id + 1
        response = self.client.post(reverse('website:question_delete',  args=(question_id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_loads_correct_template_when_not_authorized(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.post(reverse('website:question_delete', args=(question_id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')
    
    def test_view_shows_not_authorized_when_answer_exists(self):
        self.client.login(username='johndoe', password='johndoe')
        user = User.objects.get(username='johndoe')
        question = Question.objects.get(title='TestQuestion')
        answer = Answer.objects.create(question=question, uid=user.id, body='TestAnswer')
        response = self.client.get(reverse('website:question_delete', args=(question.id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_delete_question(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:question_delete', args=(question.id, )))
        question = Question.objects.get(title='TestQuestion')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(question.is_active)

    def test_view_context_title(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:question_delete', args=(question.id, )))
        self.assertTrue('title' in response.context)
        self.assertEqual(response.context['title'], question.title)

class AnswerDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        # Create two users
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        # Create a Question Category
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample Question and Answer
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        Answer.objects.create(question=question, uid=user.id, body="TestAnswer")

    def test_view_redirect_if_not_logged_in(self):
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_delete', args=(answer_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.post('/answer_delete/{0}/'.format(answer.id))
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.post(reverse('website:answer_delete', args=(answer.id, )))
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_raise_404_when_answer_not_exists(self):
        self.client.login(username="johndoe", password="johndoe")
        answer_id = Answer.objects.get(body='TestAnswer').id + 1
        response = self.client.get(reverse('website:answer_delete', args=(answer_id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_loads_correct_template_when_not_authorized(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_delete', args=(answer_id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_shows_not_authorized_when_comment_exists(self):
        self.client.login(username='johndoe', password='johndoe')
        comment_uid = User.objects.get(username='johndoe2').id
        answer = Answer.objects.get(body='TestAnswer')
        comment = AnswerComment.objects.create(answer=answer, uid=comment_uid, body='TestComment')
        response = self.client.get(reverse('website:answer_delete', args=(answer.id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_delete_answer(self):
        self.client.login(username='johndoe', password='johndoe')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.post(reverse('website:answer_delete', args=(answer.id, )))
        answer = Answer.objects.get(body='TestAnswer')
        self.assertFalse(answer.is_active)
        self.assertTrue("Answer Deleted Successfully!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

class CommentDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer comment"""
        # Create two users
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        # Create a Question Category
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample Question, Answer and Comment
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        answer = Answer.objects.create(question=question, uid=user.id, body="TestAnswer")
        AnswerComment.objects.create(uid=user.id, answer=answer, body='TestAnswerComment')

    def test_view_redirect_if_not_logged_in(self):
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(reverse('website:comment_delete', args=(comment_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_url_at_desired_location(self):
        login = self.client.login(username='johndoe', password='johndoe')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(f'/comment_delete/{comment_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')
    
    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='johndoe', password='johndoe')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(reverse('website:comment_delete', args=(comment_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')

    def test_view_raise_404_when_comment_not_exists(self):
        login = self.client.login(username='johndoe', password='johndoe')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id + 1
        response = self.client.post(reverse('website:comment_delete', args=(comment_id,)))
        self.assertEqual(response.status_code, 404)

    def test_view_loads_correct_template_when_not_authorized(self):
        self.client.login(username='johndoe2', password='johndoe2')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(reverse('website:comment_delete', args=(comment_id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_delete_comment(self):
        self.client.login(username='johndoe', password='johndoe')
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        question_id = comment.answer.question.id
        response = self.client.post(reverse('website:comment_delete', args=(comment.id,)))
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        self.assertFalse(comment.is_active)
        self.assertTrue("Comment Deleted Successfully!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

class QuestionRestoreViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create a Moderator for 'category2'
        mod2 = User.objects.create_user('mod2', 'mod2@example.com', 'mod2')
        group2 = Group.objects.create(name="TestCategory2 Group")
        moderator_group2 = ModeratorGroup.objects.create(group=group2, category=category2)
        mod2.groups.add(group2)
        # Create sample questions
        Question.objects.create(user=user, category=category1, title="TestQuestion", is_active=False)

    def test_view_redirect_if_not_logged_in(self):
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:question_restore', args=(question_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:question_restore', args=(question_id,)), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_shows_not_authorized_if_not_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:question_restore', args=(question_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_url_at_desired_location(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get('/question_restore/{0}/'.format(question_id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_url_accessible_by_name(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:question_restore', args=(question_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_raise_404_when_question_not_exists(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title='TestQuestion').id + 1
        response = self.client.get(reverse('website:question_restore', args=(question_id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_raise_404_when_question_not_deleted(self):
        question = Question.objects.get(title='TestQuestion')
        question.is_active = True
        question.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        response = self.client.get(reverse('website:question_restore', args=(question.id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_if_moderator_not_authorized(self):
        # Log in the Moderator
        self.client.login(username='mod2', password='mod2')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:question_restore', args=(question_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_restore_question(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:question_restore', args=(question.id, )))
        question = Question.objects.get(title='TestQuestion')
        self.assertTrue(question.is_active)
        self.assertTrue("Question Restored Successfully!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question.id, )))

class AnswerRestoreViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create a Moderator for 'category2'
        mod2 = User.objects.create_user('mod2', 'mod2@example.com', 'mod2')
        group2 = Group.objects.create(name="TestCategory2 Group")
        moderator_group2 = ModeratorGroup.objects.create(group=group2, category=category2)
        mod2.groups.add(group2)
        # Create sample questions
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        Answer.objects.create(question=question, uid=user.id, body="TestAnswer", is_active=False)

    def test_view_redirect_if_not_logged_in(self):
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_restore', args=(answer_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_restore', args=(answer_id,)), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_shows_not_authorized_if_not_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_restore', args=(answer_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_url_at_desired_location(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        answer = Answer.objects.get(body='TestAnswer')
        response = self.client.get('/answer_restore/{0}/'.format(answer.id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/question/{answer.question.id}/#answer{answer.id}')

    def test_view_url_accessible_by_name(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        answer = Answer.objects.get(body='TestAnswer')
        response = self.client.get(reverse('website:answer_restore', args=(answer.id, )))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/question/{answer.question.id}/#answer{answer.id}')

    def test_view_raise_404_when_answer_not_exists(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        answer_id = Answer.objects.get(body='TestAnswer').id + 1
        response = self.client.get(reverse('website:answer_restore', args=(answer_id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_raise_404_when_answer_not_deleted(self):
        answer = Answer.objects.get(body='TestAnswer')
        answer.is_active = True
        answer.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        response = self.client.get(reverse('website:answer_restore', args=(answer.id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_if_moderator_not_authorized(self):
        # Log in the Moderator
        self.client.login(username='mod2', password='mod2')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:answer_restore', args=(answer_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_if_question_not_active(self):
        question = Question.objects.get(title='TestQuestion')
        question.is_active = False
        question.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        answer = Answer.objects.get(body='TestAnswer')
        response = self.client.get(reverse('website:answer_restore', args=(answer.id, )))
        self.assertTrue("Answer can only be restored when its question is not deleted."
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question.id, )))

    def test_view_restore_answer(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        answer = Answer.objects.get(body='TestAnswer')
        response = self.client.post(reverse('website:answer_restore', args=(answer.id, )))
        answer = Answer.objects.get(body='TestAnswer')
        self.assertTrue(answer.is_active)
        self.assertTrue("Answer Restored Successfully!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/question/{answer.question.id}/#answer{answer.id}')

class CommentRestoreViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create a Moderator for 'category2'
        mod2 = User.objects.create_user('mod2', 'mod2@example.com', 'mod2')
        group2 = Group.objects.create(name="TestCategory2 Group")
        moderator_group2 = ModeratorGroup.objects.create(group=group2, category=category2)
        mod2.groups.add(group2)
        # Create sample questions
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        answer = Answer.objects.create(question=question, uid=user.id, body="TestAnswer")
        AnswerComment.objects.create(uid=user.id, answer=answer, body='TestAnswerComment', is_active=False)

    def test_view_redirect_if_not_logged_in(self):
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(reverse('website:comment_restore', args=(comment_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(reverse('website:comment_restore', args=(comment_id,)), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_shows_not_authorized_if_not_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(reverse('website:comment_restore', args=(comment_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_url_at_desired_location(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        response = self.client.get('/comment_restore/{0}/'.format(comment.id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/question/{comment.answer.question.id}/#comm{comment.id}')

    def test_view_url_accessible_by_name(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        response = self.client.get(reverse('website:comment_restore', args=(comment.id, )))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/question/{comment.answer.question.id}/#comm{comment.id}')

    def test_view_raise_404_when_comment_not_exists(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id + 1
        response = self.client.get(reverse('website:comment_restore', args=(comment_id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_raise_404_when_comment_not_deleted(self):
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        comment.is_active = True
        comment.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        response = self.client.get(reverse('website:comment_restore', args=(comment.id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_if_moderator_not_authorized(self):
        # Log in the Moderator
        self.client.login(username='mod2', password='mod2')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(reverse('website:comment_restore', args=(comment_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_if_answer_not_active(self):
        answer = Answer.objects.get(body='TestAnswer')
        answer.is_active = False
        answer.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        response = self.client.get(reverse('website:comment_restore', args=(comment.id, )))
        self.assertTrue("Comment can only be restored when its answer is not deleted."
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(answer.question.id, )))

    def test_view_restore_comment(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        response = self.client.post(reverse('website:comment_restore', args=(comment.id, )))
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        self.assertTrue(comment.is_active)
        self.assertTrue("Comment Restored Successfully!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/question/{comment.answer.question.id}/#comm{comment.id}')

class ApproveQuestionViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create a Moderator for 'category2'
        mod2 = User.objects.create_user('mod2', 'mod2@example.com', 'mod2')
        group2 = Group.objects.create(name="TestCategory2 Group")
        moderator_group2 = ModeratorGroup.objects.create(group=group2, category=category2)
        mod2.groups.add(group2)
        # Create sample questions
        Question.objects.create(user=user, category=category1, title="TestQuestion", is_spam=True)

    def test_view_redirect_if_not_logged_in(self):
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:approve_spam_question', args=(question_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:approve_spam_question', args=(question_id,)), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_redirects_if_not_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:approve_spam_question', args=(question_id,)))
        # Question not approved
        question = Question.objects.get(title='TestQuestion')
        self.assertTrue(question.is_spam)
        # View Redirects
        self.assertEqual(response.status_code, 302)

    def test_view_url_at_desired_location(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get('/approve_spam_question/{0}/'.format(question_id))
        # Question approved
        question = Question.objects.get(title='TestQuestion')
        self.assertFalse(question.is_spam)
        # View Redirects
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_url_accessible_by_name(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:approve_spam_question', args=(question_id, )))
        # Question approved
        question = Question.objects.get(title='TestQuestion')
        self.assertFalse(question.is_spam)
        # View Redirects
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))

    def test_view_raise_404_when_question_not_exists(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title='TestQuestion').id + 1
        response = self.client.get(reverse('website:approve_spam_question', args=(question_id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_raise_404_when_question_deleted(self):
        question = Question.objects.get(title='TestQuestion')
        question.is_active = False
        question.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        response = self.client.get(reverse('website:approve_spam_question', args=(question.id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_raise_404_when_question_not_spam(self):
        question = Question.objects.get(title='TestQuestion')
        question.is_spam = False
        question.save()
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        response = self.client.get(reverse('website:approve_spam_question', args=(question.id, )))
        self.assertEqual(response.status_code, 404)

    def test_view_if_moderator_not_authorized(self):
        # Log in the Moderator
        self.client.login(username='mod2', password='mod2')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:approve_spam_question', args=(question_id,)))
        # Question not approved
        question = Question.objects.get(title='TestQuestion')
        self.assertTrue(question.is_spam)
        # View Redirects
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question_id,)))

    def test_view_approve_question(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:approve_spam_question', args=(question.id, )))
        # Question Approved
        question = Question.objects.get(title='TestQuestion')
        self.assertFalse(question.is_spam)
        self.assertTrue("Question marked successfully as Not-Spam!"
                        in response.cookies['messages'].value)
        # View Redirects
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('website:get_question', args=(question.id, )))

class MarkAnswerSpamViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
         # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample Question and Answer
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        Answer.objects.create(question=question, uid=user.id, body="TestAnswer")

    def test_view_redirect_if_not_logged_in(self):
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:mark_answer_spam', args=(answer_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.get(reverse('website:mark_answer_spam', args=(answer_id, )), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='mod1', password='mod1')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.get('/mark_answer_spam/{0}/'.format(answer.id))
        self.assertRedirects(response, '/question/{0}/#answer{1}'.format(question_id, answer.id))

    def test_view_url_accessible_by_name(self):
        self.client.login(username='mod1', password='mod1')
        answer = Answer.objects.get(body='TestAnswer')
        question_id = answer.question.id
        response = self.client.get(reverse('website:mark_answer_spam', args=(answer.id, )))
        self.assertRedirects(response, '/question/{0}/#answer{1}'.format(question_id, answer.id))

    def test_view_post_answer_spam(self):
        self.client.login(username='mod1', password='mod1')
        answer_id = Answer.objects.get(body='TestAnswer').id
        self.client.post(reverse('website:mark_answer_spam', args=(answer_id, )),
                                 {'selector': 'spam'})
        answer = Answer.objects.get(id=answer_id)
        self.assertTrue(answer.is_spam)

    def test_view_post_answer_non_spam(self):
        answer = Answer.objects.get(body='TestAnswer')
        answer.is_spam = True
        answer.save()
        self.client.login(username='mod1', password='mod1')
        answer_id = Answer.objects.get(body='TestAnswer').id
        self.client.post(reverse('website:mark_answer_spam', args=(answer_id, )),
                                 {'selector': 'non-spam'})
        answer = Answer.objects.get(id=answer_id)
        self.assertFalse(answer.is_spam)

class MarkCommentSpamViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
         # Create a user
        user = User.objects.create_user('johndoe', 'johndoe@example.com', 'johndoe')
        # Create Question Categories
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample Question and Answer
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        answer = Answer.objects.create(question=question, uid=user.id, body="TestAnswer")
        AnswerComment.objects.create(answer=answer, uid=user.id, body="TestAnswerComment")

    def test_view_redirect_if_not_logged_in(self):
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(reverse('website:mark_comment_spam', args=(comment_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_not_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.get(reverse('website:mark_comment_spam', args=(comment_id, )), follow=True)
        self.assertRedirects(response, reverse('website:home'))

    def test_view_url_at_desired_location(self):
        self.client.login(username='mod1', password='mod1')
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        question_id = comment.answer.question.id
        response = self.client.get('/mark_comment_spam/{0}/'.format(comment.id))
        self.assertRedirects(response, '/question/{0}/#comm{1}'.format(question_id, comment.id))

    def test_view_url_accessible_by_name(self):
        self.client.login(username='mod1', password='mod1')
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        question_id = comment.answer.question.id
        response = self.client.get(reverse('website:mark_comment_spam', args=(comment.id, )))
        self.assertRedirects(response, '/question/{0}/#comm{1}'.format(question_id, comment.id))

    def test_view_post_comment_spam(self):
        self.client.login(username='mod1', password='mod1')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        self.client.post(reverse('website:mark_comment_spam', args=(comment_id, )),
                                 {'choice': 'spam'})
        comment = AnswerComment.objects.get(id=comment_id)
        self.assertTrue(comment.is_spam)

    def test_view_post_comment_non_spam(self):
        comment = AnswerComment.objects.get(body='TestAnswerComment')
        comment.is_spam = True
        comment.save()
        self.client.login(username='mod1', password='mod1')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        self.client.post(reverse('website:mark_comment_spam', args=(comment_id, )),
                                 {'choice': 'non-spam'})
        comment = AnswerComment.objects.get(id=comment_id)
        self.assertFalse(comment.is_spam)

class SearchViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Setup test data"""
        # Create a Question Category
        category1 = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
    
    def test_view_url_at_desired_location(self):
        response = self.client.get('/search/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('website:search'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('website:search'))
        self.assertTemplateUsed(response, 'website/templates/search.html')

    def test_view_redirects_if_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        response = self.client.get(reverse('website:search'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/moderator/')
    
    def test_view_context_category(self):
        response = self.client.get(reverse('website:search'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'],
                                 ['<FossCategory: TestCategory>'])

class FilterViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        category2 = FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")
        Question.objects.create(user=user, category=category, sub_category='TestSubCategory', title="TestQuestion2")
        Question.objects.create(user=user, category=category2, title="TestQuestion3")
        Question.objects.create(user=user, category=category2, title="TestQuestion4", is_spam=True)

    def test_view_url_at_desired_location(self):
        response = self.client.get('/filter/TestCategory/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('website:filter', args=('TestCategory', )))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('website:filter', args=('TestCategory', )))
        self.assertTemplateUsed(response, 'website/templates/filter.html')

    def test_view_context_category(self):
        response = self.client.get(reverse('website:filter', args=('TestCategory', )))
        self.assertTrue('category' in response.context)
        self.assertEqual(response.context['category'], 'TestCategory')

    def test_view_context_tutorial(self):
        response = self.client.get(reverse('website:filter', args=('TestCategory', 'TestSubCategory', )))
        self.assertTrue('tutorial' in response.context)
        self.assertEqual(response.context['tutorial'], 'TestSubCategory')

    def test_view_context_questions_by_category(self):
        response = self.client.get(reverse('website:filter', args=('TestCategory', )))
        question_id = Question.objects.get(title='TestQuestion').id
        question2_id = Question.objects.get(title='TestQuestion2').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                 ['<Question: {0} - TestCategory - TestSubCategory - TestQuestion2 - johndoe>'.format(question2_id),
                                  '<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

    def test_view_context_questions_by_category_tutorial(self):
        response = self.client.get(reverse('website:filter', args=('TestCategory', 'TestSubCategory', )))
        question2_id = Question.objects.get(title='TestQuestion2').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                 ['<Question: {0} - TestCategory - TestSubCategory - TestQuestion2 - johndoe>'.format(question2_id)])

    def test_view_context_questions_by_category_moderator_activated(self):
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        response = self.client.get(reverse('website:filter', args=('TestCategory2', )))
        question_id = Question.objects.get(title='TestQuestion3').id
        question2_id = Question.objects.get(title='TestQuestion4').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                 ['<Question: {0} - TestCategory2 -  - TestQuestion4 - johndoe>'.format(question2_id),
                                  '<Question: {0} - TestCategory2 -  - TestQuestion3 - johndoe>'.format(question_id)])

class UserNotificationsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        # Create two users
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe", first_name="John", last_name="John")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        # Create a Question Category
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample question and notification
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        Notification.objects.create(uid=user.id, qid=question.id)

    def test_view_redirect_if_not_logged_in(self):
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('website:user_notifications', args=(user_id, )))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_no_fullname(self):
        user_id = User.objects.get(username='johndoe2').id
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get(reverse('website:user_notifications', args=(user_id, )))
        self.assertRedirects(response, '/accounts/profile/?next=/user/{0}/notifications/'.format(user_id))

    def test_view_if_unauthorized_user(self):
        self.client.login(username='mod1', password='mod1')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('website:user_notifications', args=(user_id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_if_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('website:user_notifications', args=(user_id, )))
        self.assertTrue("Moderators cannot access the Notifications!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/moderator/')

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get('/user/{0}/notifications/'.format(user_id))
        self.assertEqual(response.status_code, 302)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('website:user_notifications', args=(user_id, )))
        self.assertEqual(response.status_code, 302)

    def test_view_uses_correct_template(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('website:user_notifications', args=(user_id, )))
        self.assertTemplateUsed(response, 'website/templates/notifications.html')

    def test_view_context_notifications(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('website:user_notifications', args=(user_id, )))
        self.assertTrue('notifications' in response.context)
        notification_id = Notification.objects.get(uid=user_id)
        self.assertQuerysetEqual(response.context['notifications'],
                                 ['<Notification: {0}>'.format(notification_id)])

class ClearNotificationsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        # Create a user
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        # Create a Question Category
        category1 = FossCategory.objects.create(name="TestCategory1", email="category1@example.com")
        # Create a Moderator for 'category1'
        mod1 = User.objects.create_user('mod1', 'mod1@example.com', 'mod1')
        group1 = Group.objects.create(name="TestCategory1 Group")
        moderator_group1 = ModeratorGroup.objects.create(group=group1, category=category1)
        mod1.groups.add(group1)
        # Create sample question and notification
        question = Question.objects.create(user=user, category=category1, title="TestQuestion")
        Notification.objects.create(uid=user.id, qid=question.id)

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:clear_notifications'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_if_moderator_activated(self):
        # Log in the Moderator
        self.client.login(username='mod1', password='mod1')
        # Activating Moderator Panel
        session = self.client.session
        session['MODERATOR_ACTIVATED'] = True
        session.save()
        response = self.client.get(reverse('website:clear_notifications'))
        self.assertTrue("Moderators cannot clear the Notifications!"
                        in response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/moderator/')

    def test_view_url_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get('/clear-notifications/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:clear_notifications'))
        self.assertEqual(response.status_code, 302)

    def test_view_notifications_deleted(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('website:clear_notifications'))
        try:
            Notification.objects.get(uid=user_id)
            self.fail('Notifications not deleted.')
        except:
            self.assertEqual(response.status_code, 302)

class AjaxTutorialsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = FossCategory.objects.create(name='TestCategory', email='category@example.com')
        FossCategory.objects.create(name='TestCategory2', email='category2@example.com')
        SubFossCategory.objects.create(parent=category, name='TestSubCategory')

    def test_view_get_error_at_desired_location(self):
        response = self.client.get('/ajax-tutorials/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')
    
    def test_view_get_error_accessible_by_name(self):
        response = self.client.get(reverse('website:ajax_tutorials'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')

    def test_view_post_category_without_subcat(self):
        category_id = FossCategory.objects.get(name='TestCategory2').id
        response = self.client.post(reverse('website:ajax_tutorials'),
                                    {'category': category_id})
        self.assertContains(response, 'No sub-category in category.')

    def test_view_post_context_category_with_subcat(self):
        category_id = FossCategory.objects.get(name='TestCategory').id
        response = self.client.post(reverse('website:ajax_tutorials'),
                                    {'category': category_id})
        self.assertTrue('tutorials' in response.context)
        self.assertQuerysetEqual(response.context['tutorials'],
                                 ['<SubFossCategory: TestSubCategory>'])

    def test_view_post_category_with_subcat_uses_correct_template(self):
        category_id = FossCategory.objects.get(name='TestCategory').id
        response = self.client.post(reverse('website:ajax_tutorials'),
                                    {'category': category_id})
        self.assertTemplateUsed(response, 'website/templates/ajax-tutorials.html')

class AjaxNotificationRemoveViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        Notification.objects.create(uid = user.id, qid = question.id)

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:ajax_notification_remove'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_get_error_at_desired_location(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get('/ajax-notification-remove/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')
    
    def test_view_get_error_accessible_by_name(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:ajax_notification_remove'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')

    def test_view_post_notification_no_exists(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        question_id = Question.objects.get(title='TestQuestion').id
        notification_id = Notification.objects.get(uid=user_id, qid=question_id).id + 1
        response = self.client.post(reverse('website:ajax_notification_remove'),
                                    {'notification_id': notification_id})
        self.assertContains(response, 'Notification not found.')

    def test_view_post_unauthorized_user(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user_id = User.objects.get(username='johndoe').id
        question_id = Question.objects.get(title='TestQuestion').id
        notification_id = Notification.objects.get(uid=user_id, qid=question_id).id
        response = self.client.post(reverse('website:ajax_notification_remove'),
                                    {'notification_id': notification_id})
        self.assertContains(response, 'Unauthorized user.')
    
    def test_view_post_success(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        question_id = Question.objects.get(title='TestQuestion').id
        notification_id = Notification.objects.get(uid=user_id, qid=question_id).id
        response = self.client.post(reverse('website:ajax_notification_remove'),
                                    {'notification_id': notification_id})
        self.assertContains(response, 'removed')

class AjaxKeywordSearchViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_view_get_error_at_desired_location(self):
        response = self.client.get('/ajax-keyword-search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')
    
    def test_view_get_error_accessible_by_name(self):
        response = self.client.get(reverse('website:ajax_keyword_search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-requests-not-allowed.html')

    def test_view_post_context_questions(self):
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.post(reverse('website:ajax_keyword_search'),
                                    {'key':'Test'})
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                 ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

    def test_view_loads_correct_template(self):
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.post(reverse('website:ajax_keyword_search'),
                                    {'key':'Test'})
        self.assertTemplateUsed(response, 'website/templates/ajax-keyword-search.html')

class AjaxVotePostViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:ajax_vote_post'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_vote_same_user(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question_id, 'action': 'vote', 'type': 'up'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question_id, 'action': 'vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)

    def test_view_recall_vote_same_user(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question_id, 'action': 'recall-vote', 'type': 'up'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question_id, 'action': 'recall-vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)

    def test_view_vote(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        question_id = Question.objects.get(title='TestQuestion').id
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question_id, 'action': 'vote', 'type': 'up'})
        question = Question.objects.get(title='TestQuestion')
        self.assertEqual(question.num_votes, 1)
        question.userUpVotes.remove(user)
        question.num_votes = 0
        question.save()
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question_id, 'action': 'vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, -1)

    def test_view_vote_when_already_voted(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        question = Question.objects.get(title='TestQuestion')
        question.userDownVotes.add(user)
        question.num_votes = -1
        question.save()
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question.id, 'action': 'vote', 'type': 'up'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 1)
        question.userDownVotes.remove(user)
        question.userUpVotes.add(user)
        question.num_votes = 1
        question.save()
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question.id, 'action': 'vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, -1)

    def test_view_recall_vote(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        question = Question.objects.get(title='TestQuestion')
        question.userUpVotes.add(user)
        question.num_votes = 1
        question.save()
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question.id, 'action': 'recall-vote', 'type': 'up'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)
        question.userDownVotes.add(user)
        question.userUpVotes.remove(user)
        question.num_votes = -1
        question.save()
        self.client.post(reverse('website:ajax_vote_post'),
                         {'id': question.id, 'action': 'recall-vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)

class AjaxAnsVotePostViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        Answer.objects.create(question=question, uid=user.id, body='TestAnswerBody')

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:ajax_ans_vote_post'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_vote_same_user(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswerBody').id
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer_id, 'action': 'vote', 'type': 'up'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer_id, 'action': 'vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)

    def test_view_recall_vote_same_user(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswerBody').id
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer_id, 'action': 'recall-vote', 'type': 'up'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer_id, 'action': 'recall-vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)

    def test_view_vote(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        answer_id = Answer.objects.get(body='TestAnswerBody').id
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer_id, 'action': 'vote', 'type': 'up'})
        answer = Answer.objects.get(body='TestAnswerBody')
        self.assertEqual(answer.num_votes, 1)
        answer.userUpVotes.remove(user)
        answer.num_votes = 0
        answer.save()
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer_id, 'action': 'vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, -1)

    def test_view_vote_when_already_voted(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        answer = Answer.objects.get(body='TestAnswerBody')
        answer.userDownVotes.add(user)
        answer.num_votes = -1
        answer.save()
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer.id, 'action': 'vote', 'type': 'up'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 1)
        answer.userDownVotes.remove(user)
        answer.userUpVotes.add(user)
        answer.num_votes = 1
        answer.save()
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer.id, 'action': 'vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, -1)

    def test_view_recall_vote(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        answer = Answer.objects.get(body='TestAnswerBody')
        answer.userUpVotes.add(user)
        answer.num_votes = 1
        answer.save()
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer.id, 'action': 'recall-vote', 'type': 'up'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)
        answer.userDownVotes.add(user)
        answer.userUpVotes.remove(user)
        answer.num_votes = -1
        answer.save()
        self.client.post(reverse('website:ajax_ans_vote_post'),
                         {'id': answer.id, 'action': 'recall-vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)
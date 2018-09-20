from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.conf import settings
from website.models import *
from website.forms import *

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
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                    ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

    def test_view_context_categories(self):
        response = self.client.get(reverse('website:home'))
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
        self.assertTemplateUsed(response, 'website/templates/questions.html')

    def test_view_context_questions(self):
        response = self.client.get(reverse('website:home'))
        question_id = Question.objects.get(title="TestQuestion").id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],
                                    ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

class GetQuestionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion",\
                                            sub_category="TestSubCategory", num_votes=1)
        answer = Answer.objects.create(question=question, uid=user.id, body="TestAnswer")
        Answer.objects.create(question=question, uid=user.id, body="TestAnswer2", is_spam=True)
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
        self.assertTemplateUsed(response, 'website/templates/get-question.html')

    def test_view_context_question(self):
        question = Question.objects.get(title="TestQuestion")
        response = self.client.get(reverse('website:get_question', args=(question.id,)))
        self.assertTrue('question' in response.context)
        self.assertEqual(response.context['question'], question)

    def test_view_context_ans_count(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('ans_count' in response.context)
        self.assertEqual(response.context['ans_count'], 1)

    def test_view_context_ans_count_moderator_activated(self):
        settings.MODERATOR_ACTIVATED = True
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('ans_count' in response.context)
        self.assertEqual(response.context['ans_count'], 2)
        settings.MODERATOR_ACTIVATED = False

    def test_view_context_sub_category(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('sub_category' in response.context)
        self.assertEqual(response.context['sub_category'], True)

    def test_view_context_main_list(self):
        question_id = Question.objects.get(title="TestQuestion").id
        answer = Answer.objects.get(body = "TestAnswer")
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('main_list' in response.context)
        self.assertEqual(response.context['main_list'], [(answer, [0,0,0])])

    def test_view_context_main_list_moderator_activated(self):
        settings.MODERATOR_ACTIVATED = True
        question_id = Question.objects.get(title='TestQuestion').id
        answer = Answer.objects.get(body = 'TestAnswer')
        answer2 = Answer.objects.get(body = 'TestAnswer2')
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('main_list' in response.context)
        self.assertEqual(response.context['main_list'], [(answer, [0,0,0]), (answer2, [0,0,0])])
        settings.MODERATOR_ACTIVATED = False

    def test_view_context_form(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], AnswerQuestionForm)

    def test_view_context_thisUserUpvote(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('thisUserUpvote' in response.context)
        self.assertEqual(response.context['thisUserUpvote'], 0)

    def test_view_context_thisUserDownvote(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('thisUserDownvote' in response.context)
        self.assertEqual(response.context['thisUserDownvote'], 0)

    def test_view_context_net_count(self):
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get(reverse('website:get_question', args=(question_id,)))
        self.assertTrue('net_count' in response.context)
        self.assertEqual(response.context['net_count'], 1)

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

    def test_view_url_loads_with_correct_template(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.get('/question-answer/{0}/'.format(question_id))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('website:question_answer', args=(question_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/get-question.html')

    def test_view_post_no_answer(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),\
                                        {'question': question_id})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Answer field required')

    def test_view_post_too_short_body(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),\
                                    {'body': 'TooShort', 'question': question_id})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body should be minimum 12 characters long')

    def test_view_post_body_only_spaces(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),\
                                    {'body': '        &nbsp;          ', 'question': question_id})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only spaces')

    def test_view_post_body_only_tags(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),\
                                    {'body': '<p><div></div></p>        ', 'question': question_id})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only tags')

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

    def test_view_post_valid_data(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title="TestQuestion").id
        response = self.client.post(reverse('website:question_answer', args=(question_id,)),\
                                    {'body': 'Test question body', 'question': question_id})
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
        response = self.client.get(reverse('website:answer_comment'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_no_fullname(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:answer_comment'))
        self.assertRedirects(response, '/accounts/profile/?next=/answer-comment/')

    def test_view_does_not_load(self):
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get(reverse('website:answer_comment'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')

    def test_view_post_body_only_spaces(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer_id = Answer.objects.get(body="TestAnswer").id
        response = self.client.post(reverse('website:answer_comment'),\
                                    {'body': '        &nbsp;          ', 'answer_id': answer_id})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only spaces')

    def test_view_post_body_only_tags(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer_id = Answer.objects.get(body="TestAnswer").id
        response = self.client.post(reverse('website:answer_comment'),\
                                    {'body': '<p><div></div></p>     ', 'answer_id': answer_id})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only tags')

    def test_view_post_notification_created_answer_creator(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer = Answer.objects.get(body="TestAnswer")
        self.client.post(reverse('website:answer_comment'),\
                                    {'body': 'Test Answer comment', 'answer_id': answer.id})
        try:
            user_id = User.objects.get(username='johndoe').id
            notification = Notification.objects.get(uid=user_id, qid=answer.question.id, aid=answer.id)
            self.assertIsInstance(notification, Notification)
        except:
            self.fail('Notification not created for answer creator.')

    def test_view_post_notification_created_comment_creators(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer = Answer.objects.get(body="TestAnswer")
        self.client.post(reverse('website:answer_comment'),\
                                    {'body': 'Test Answer comment', 'answer_id': answer.id})
        try:
            user_id = User.objects.get(username='johndoe3').id
            notification = Notification.objects.get(uid=user_id, qid=answer.question.id, aid=answer.id)
            self.assertIsInstance(notification, Notification)
        except:
            self.fail('Notification not created for comment creators.')

    def test_view_post_valid_data(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer = Answer.objects.get(body="TestAnswer")
        response = self.client.post(reverse('website:answer_comment'),\
                                    {'body': 'Test Answer comment', 'answer_id': answer.id})
        self.assertRedirects(response, reverse('website:get_question', args=(answer.question.id, )))

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
        self.assertQuerysetEqual(response.context['questions'],\
                                    ['<Question: {0} - TestCategory - TestSubCategory - TestQuestion2 - johndoe>'.format(question2_id),\
                                    '<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

    def test_view_context_questions_by_category_tutorial(self):
        response = self.client.get(reverse('website:filter', args=('TestCategory', 'TestSubCategory', )))
        question2_id = Question.objects.get(title='TestQuestion2').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],\
                                    ['<Question: {0} - TestCategory - TestSubCategory - TestQuestion2 - johndoe>'.format(question2_id)])

    def test_view_context_questions_by_category_moderator_activated(self):
        settings.MODERATOR_ACTIVATED = True
        response = self.client.get(reverse('website:filter', args=('TestCategory2', )))
        settings.MODERATOR_ACTIVATED = False
        question_id = Question.objects.get(title='TestQuestion3').id
        question2_id = Question.objects.get(title='TestQuestion4').id
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],\
                                    ['<Question: {0} - TestCategory2 -  - TestQuestion4 - johndoe>'.format(question2_id),\
                                    '<Question: {0} - TestCategory2 -  - TestQuestion3 - johndoe>'.format(question_id)])

class NewQuestionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2", first_name="John", last_name="Doe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:new_question'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_redirect_if_no_fullname(self):
        self.client.login(username='johndoe', password='johndoe')
        response = self.client.get(reverse('website:new_question'))
        self.assertRedirects(response, '/accounts/profile/?next=/new-question/')

    def test_view_url_loads_with_correct_template(self):
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.get('/new-question/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('website:new_question'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/new-question.html')

    def test_view_post_no_category(self):
        self.client.login(username='johndoe2', password='johndoe2')
        response = self.client.post(reverse('website:new_question'),\
                                    {'title': 'Test question title', 'body': 'Test question body',\
                                    'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'category', 'Select a category')

    def test_view_post_no_title(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'body': 'Test question body',\
                                    'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title field required')

    def test_view_post_no_body(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'title': 'Test question title',\
                                    'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Question field required')

    def test_view_post_title_only_spaces(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'title': '  &nbsp;             ',\
                                    'body': 'Test question body', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title cannot be only spaces')

    def test_view_post_title_only_tags(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'title': '<p><div></div></p>',\
                                    'body': 'Test question body', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title cannot be only tags')

    def test_view_post_title_too_short(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'title': 'TooShort',\
                                    'body': 'Test question body', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title should be longer than 12 characters')

    def test_view_post_title_already_exists(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'title': 'TestQuestion',\
                                    'body': 'Test question body', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'This title already exists')

    def test_view_post_body_only_spaces(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'title': 'Test question title',\
                                    'body': '           &nbsp;     ', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only spaces')

    def test_view_post_body_only_tags(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'body': '<p><div></div></p>',\
                                    'title': 'Test question title', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only tags')

    def test_view_post_body_too_short(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'body': 'TooShort',\
                                    'title': 'Test question title', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body should be minimum 12 characters long')

    def test_view_post_spam_question(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'body': 'swiss replica watches buy',\
                                    'title': 'Test question title', 'tutorial':  None})
        self.assertRedirects(response, reverse('website:home'))

    def test_view_post_valid_data(self):
        self.client.login(username='johndoe2', password='johndoe2')
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'body': 'Test question body',\
                                    'title': 'Test question title', 'tutorial':  None})
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
        category = FossCategory.objects.get(name='TestCategory')
        response = self.client.post(reverse('website:new_question'),\
                                    {'category': category.id, 'body': 'TooShort',\
                                    'title': 'Test question title', 'tutorial':  None})
        self.assertTrue('category' in response.context)
        self.assertEqual(int(response.context['category']), category.id)
        self.assertTrue('tutorial' in response.context)
        self.assertEqual(response.context['tutorial'], 'None')
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], NewQuestionForm)

class EditQuestionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe", first_name="John", last_name="Doe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        User.objects.create_user("johndoe3", "johndoe3@example.com", "johndoe3", first_name="John", last_name="Doe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        FossCategory.objects.create(name="TestCategory2", email="category2@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

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

    def test_view_redirects_when_not_authorized(self):
        self.client.login(username='johndoe3', password='johndoe3')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:edit_question', args=(question_id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')
    
    def test_view_redirects_when_answer_exists(self):
        self.client.login(username='johndoe', password='johndoe')
        user = User.objects.get(username='johndoe')
        question = Question.objects.get(title='TestQuestion')
        answer = Answer.objects.create(question=question, uid=user.id, body='TestAnswer')
        response = self.client.get(reverse('website:edit_question', args=(question.id, )))
        answer.delete()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_post_no_category(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.post(reverse('website:edit_question', args=(question_id, )),\
                                    {'title': 'Test question title', 'body': 'Test question body',\
                                    'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'category', 'Select a category')

    def test_view_post_no_title(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'body': 'Test question body',\
                                    'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title field required')

    def test_view_post_no_body(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'title': 'Test question title',\
                                    'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Question field required')

    def test_view_post_title_only_spaces(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'title': '  &nbsp;             ',\
                                    'body': 'Test question body', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title cannot be only spaces')

    def test_view_post_title_only_tags(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'title': '<p><div></div></p>',\
                                    'body': 'Test question body', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title cannot be only tags')

    def test_view_post_title_too_short(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'title': 'TooShort',\
                                    'body': 'Test question body', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Title should be longer than 12 characters')

    def test_view_post_body_only_spaces(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'title': 'Test question title',\
                                    'body': '           &nbsp;     ', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only spaces')

    def test_view_post_body_only_tags(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'body': '<p><div></div></p>',\
                                    'title': 'Test question title', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body cannot be only tags')

    def test_view_post_body_too_short(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'body': 'TooShort',\
                                    'title': 'Test question title', 'tutorial':  None})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'body', 'Body should be minimum 12 characters long')

    def test_view_post_title_exists_allowed(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'title': 'TestQuestion',\
                                    'body': 'Test question body', 'tutorial':  None})
        self.assertRedirects(response, reverse('website:get_question', args=(question.id, )))

    def test_view_post_mark_spam(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'title': 'TestQuestion',\
                                    'body': 'Test question body', 'tutorial':  None, 'is_spam': True})
        self.assertRedirects(response, reverse('website:home'))

    def test_view_post_mark_spam_moderator_activated(self):
        settings.MODERATOR_ACTIVATED = True
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'title': 'TestQuestion',\
                                    'body': 'Test question body', 'tutorial':  None, 'is_spam': True})
        self.assertRedirects(response, reverse('website:get_question', args=(question.id, )))
        settings.MODERATOR_ACTIVATED = False

    def test_view_get_context(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:edit_question', args=(question_id, )))
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], NewQuestionForm)

    def test_view_post_context_when_form_error(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.post(reverse('website:edit_question', args=(question.id, )),\
                                    {'category': question.category.id, 'body': 'TooShort',\
                                    'title': 'Test question title', 'tutorial':  None})
        self.assertTrue('category' in response.context)
        self.assertEqual(int(response.context['category']), question.category.id)
        self.assertTrue('tutorial' in response.context)
        self.assertEqual(response.context['tutorial'], 'None')
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], NewQuestionForm)

    def test_view_post_change_data(self):
        settings.MODERATOR_ACTIVATED = True
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        category = FossCategory.objects.get(name='TestCategory2')
        response = self.client.post(reverse('website:edit_question', args=(question_id, )),\
                                    {'category': category.id, 'title': 'Test question title',\
                                    'body': 'Test question body changed', 'tutorial':  'TestTutorial',\
                                    'is_spam': True})
        self.assertRedirects(response, reverse('website:get_question', args=(question_id, )))
        settings.MODERATOR_ACTIVATED = False
        question = Question.objects.get(id = question_id)
        self.assertEqual(question.category, category)
        self.assertEqual(question.title, 'Test question title')
        self.assertEqual(question.body, 'Test question body changed')
        self.assertEqual(question.sub_category, 'TestTutorial')
        self.assertTrue(question.is_spam)

class QuestionDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        user2 = User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

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
        response = self.client.get(reverse('website:question_delete', args=(question_id, )))
        self.assertTemplateUsed(response, 'website/templates/question-delete.html')

    def test_view_redirects_when_not_authorized(self):
        self.client.login(username='johndoe2', password='johndoe2')
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.get(reverse('website:question_delete', args=(question_id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')
    
    def test_view_redirects_when_answer_exists(self):
        self.client.login(username='johndoe', password='johndoe')
        user = User.objects.get(username='johndoe')
        question = Question.objects.get(title='TestQuestion')
        answer = Answer.objects.create(question=question, uid=user.id, body='TestAnswer')
        response = self.client.get(reverse('website:question_delete', args=(question.id, )))
        answer.delete()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

    def test_view_delete_question(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.get(reverse('website:question_delete', args=(question.id, )))
        try:
            question = Question.objects.get(title='TestQuestion')
            self.fail('Question not deleted.')
        except:
            self.assertEqual(response.status_code, 200)

    def test_view_context_title(self):
        self.client.login(username='johndoe', password='johndoe')
        question = Question.objects.get(title='TestQuestion')
        response = self.client.get(reverse('website:question_delete', args=(question.id, )))
        self.assertTrue('title' in response.context)
        self.assertEqual(response.context['title'], question.title)

class VotePostViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:vote_post'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_vote_same_user(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        self.client.post(reverse('website:vote_post'), {'id': question_id,\
                                    'action': 'vote', 'type': 'up'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)
        self.client.post(reverse('website:vote_post'), {'id': question_id,\
                                    'action': 'vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)

    def test_view_recall_vote_same_user(self):
        self.client.login(username='johndoe', password='johndoe')
        question_id = Question.objects.get(title='TestQuestion').id
        self.client.post(reverse('website:vote_post'), {'id': question_id,\
                                    'action': 'recall-vote', 'type': 'up'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)
        self.client.post(reverse('website:vote_post'), {'id': question_id,\
                                    'action': 'recall-vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)

    def test_view_vote(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        question_id = Question.objects.get(title='TestQuestion').id
        self.client.post(reverse('website:vote_post'), {'id': question_id,\
                                    'action': 'vote', 'type': 'up'})
        question = Question.objects.get(title='TestQuestion')
        self.assertEqual(question.num_votes, 1)
        question.userUpVotes.remove(user)
        question.num_votes = 0
        question.save()
        self.client.post(reverse('website:vote_post'), {'id': question_id,\
                                    'action': 'vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, -1)

    def test_view_vote_when_already_voted(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        question = Question.objects.get(title='TestQuestion')
        question.userDownVotes.add(user)
        question.num_votes = -1
        question.save()
        self.client.post(reverse('website:vote_post'), {'id': question.id,\
                                    'action': 'vote', 'type': 'up'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 1)
        question.userDownVotes.remove(user)
        question.userUpVotes.add(user)
        question.num_votes = 1
        question.save()
        self.client.post(reverse('website:vote_post'), {'id': question.id,\
                                    'action': 'vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, -1)

    def test_view_recall_vote(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        question = Question.objects.get(title='TestQuestion')
        question.userUpVotes.add(user)
        question.num_votes = 1
        question.save()
        self.client.post(reverse('website:vote_post'), {'id': question.id,\
                                    'action': 'recall-vote', 'type': 'up'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)
        question.userDownVotes.add(user)
        question.userUpVotes.remove(user)
        question.num_votes = -1
        question.save()
        self.client.post(reverse('website:vote_post'), {'id': question.id,\
                                    'action': 'recall-vote', 'type': 'down'})
        question_votes = Question.objects.get(title='TestQuestion').num_votes
        self.assertEqual(question_votes, 0)

class AnsVotePostViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        Answer.objects.create(question=question, uid=user.id, body='TestAnswerBody')

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:ans_vote_post'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_view_vote_same_user(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswerBody').id
        self.client.post(reverse('website:ans_vote_post'), {'id': answer_id,\
                                    'action': 'vote', 'type': 'up'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)
        self.client.post(reverse('website:ans_vote_post'), {'id': answer_id,\
                                    'action': 'vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)

    def test_view_recall_vote_same_user(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswerBody').id
        self.client.post(reverse('website:ans_vote_post'), {'id': answer_id,\
                                    'action': 'recall-vote', 'type': 'up'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)
        self.client.post(reverse('website:ans_vote_post'), {'id': answer_id,\
                                    'action': 'recall-vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)

    def test_view_vote(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        answer_id = Answer.objects.get(body='TestAnswerBody').id
        self.client.post(reverse('website:ans_vote_post'), {'id': answer_id,\
                                    'action': 'vote', 'type': 'up'})
        answer = Answer.objects.get(body='TestAnswerBody')
        self.assertEqual(answer.num_votes, 1)
        answer.userUpVotes.remove(user)
        answer.num_votes = 0
        answer.save()
        self.client.post(reverse('website:ans_vote_post'), {'id': answer_id,\
                                    'action': 'vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, -1)

    def test_view_vote_when_already_voted(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        answer = Answer.objects.get(body='TestAnswerBody')
        answer.userDownVotes.add(user)
        answer.num_votes = -1
        answer.save()
        self.client.post(reverse('website:ans_vote_post'), {'id': answer.id,\
                                    'action': 'vote', 'type': 'up'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 1)
        answer.userDownVotes.remove(user)
        answer.userUpVotes.add(user)
        answer.num_votes = 1
        answer.save()
        self.client.post(reverse('website:ans_vote_post'), {'id': answer.id,\
                                    'action': 'vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, -1)

    def test_view_recall_vote(self):
        self.client.login(username='johndoe2', password='johndoe2')
        user = User.objects.get(username='johndoe2')
        answer = Answer.objects.get(body='TestAnswerBody')
        answer.userUpVotes.add(user)
        answer.num_votes = 1
        answer.save()
        self.client.post(reverse('website:ans_vote_post'), {'id': answer.id,\
                                    'action': 'recall-vote', 'type': 'up'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)
        answer.userDownVotes.add(user)
        answer.userUpVotes.remove(user)
        answer.num_votes = -1
        answer.save()
        self.client.post(reverse('website:ans_vote_post'), {'id': answer.id,\
                                    'action': 'recall-vote', 'type': 'down'})
        answer_votes = Answer.objects.get(body='TestAnswerBody').num_votes
        self.assertEqual(answer_votes, 0)

class UserNotificationsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe", first_name="John", last_name="John")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        User.objects.create_user("johndoe3", "johndoe3@example.com", "johndoe3", first_name="John", last_name="Doe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
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
        self.client.login(username='johndoe3', password='johndoe3')
        user_id = User.objects.get(username='johndoe').id
        response = self.client.get(reverse('website:user_notifications', args=(user_id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/not-authorized.html')

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
        self.assertQuerysetEqual(response.context['notifications'],\
                            ['<Notification: {0}>'.format(notification_id)])

class ClearNotificationsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        Notification.objects.create(uid=user.id, qid=question.id)

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('website:clear_notifications'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

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

class SearchViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Setup test data"""
        FossCategory.objects.create(name="TestCategory", email="category@example.com")
    
    def test_view_url_at_desired_location(self):
        response = self.client.get('/search/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('website:search'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('website:search'))
        self.assertTemplateUsed(response, 'website/templates/search.html')
    
    def test_view_context_category(self):
        response = self.client.get(reverse('website:search'))
        self.assertTrue('categories' in response.context)
        self.assertQuerysetEqual(response.context['categories'],\
                                    ['<FossCategory: TestCategory>'])

class AjaxTutorialsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = FossCategory.objects.create(name='TestCategory', email='category@example.com')
        FossCategory.objects.create(name='TestCategory2', email='category2@example.com')
        SubFossCategory.objects.create(parent=category, name='TestSubCategory')

    def test_view_get_error_at_desired_location(self):
        response = self.client.get('/ajax-tutorials/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')
    
    def test_view_get_error_accessible_by_name(self):
        response = self.client.get(reverse('website:ajax_tutorials'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')

    def test_view_post_category_without_subcat(self):
        category_id = FossCategory.objects.get(name='TestCategory2').id
        response = self.client.post(reverse('website:ajax_tutorials'),\
            {'category': category_id})
        self.assertContains(response, 'No sub-category in category.')

    def test_view_post_context_category_with_subcat(self):
        category_id = FossCategory.objects.get(name='TestCategory').id
        response = self.client.post(reverse('website:ajax_tutorials'),\
            {'category': category_id})
        self.assertTrue('tutorials' in response.context)
        self.assertQuerysetEqual(response.context['tutorials'],\
            ['<SubFossCategory: TestSubCategory>'])

    def test_view_post_category_with_subcat_uses_correct_template(self):
        category_id = FossCategory.objects.get(name='TestCategory').id
        response = self.client.post(reverse('website:ajax_tutorials'),\
            {'category': category_id})
        self.assertTemplateUsed(response, 'website/templates/ajax-tutorials.html')

class AjaxAnswerUpdateViewTest(TestCase):

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

    def test_view_get_error_at_desired_location(self):
        response = self.client.get('/ajax-answer-update/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')
    
    def test_view_get_error_accessible_by_name(self):
        response = self.client.get(reverse('website:ajax_answer_update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')

    def test_view_post_answer_no_exists(self):
        answer_id = Answer.objects.get(body='TestAnswer').id + 1
        response = self.client.post(reverse('website:ajax_answer_update'),\
            {'answer_id': answer_id, 'answer_body': 'TestAnswerBody'})
        self.assertContains(response, 'Answer not found.')

    def test_view_post_answer_update_no_logged_in(self):
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.post(reverse('website:ajax_answer_update'),\
            {'answer_id': answer_id, 'answer_body': 'TestAnswerBody'})
        self.assertContains(response, 'Only moderator can update.')

    def test_view_post_answer_update_no_moderator(self):
        self.client.login(username='johndoe2', password='johndoe2')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.post(reverse('website:ajax_answer_update'),\
            {'answer_id': answer_id, 'answer_body': 'TestAnswerBody'})
        self.assertContains(response, 'Only moderator can update.')
        
    def test_view_post_answer_update_with_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        answer_id = Answer.objects.get(body='TestAnswer').id
        response = self.client.post(reverse('website:ajax_answer_update'),\
            {'answer_id': answer_id, 'answer_body': 'TestAnswerBody'})
        self.assertContains(response, 'saved')

class AjaxAnswerCommentDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer comment"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        User.objects.create_user("johndoe2", "johndoe2@example.com", "johndoe2")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        group = Group.objects.create(name="TestCategory_moderator")
        ModeratorGroup.objects.create(group=group, category=category)
        user.groups.add(group)
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        answer = Answer.objects.create(question=question, uid=user.id, body="TestAnswer")
        AnswerComment.objects.create(uid=user.id, answer=answer, body='TestAnswerComment')

    def test_view_get_error_at_desired_location(self):
        response = self.client.get('/ajax-answer-comment-delete/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')
    
    def test_view_get_error_accessible_by_name(self):
        response = self.client.get(reverse('website:ajax_answer_comment_delete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')

    def test_view_post_comment_no_exists(self):
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id + 1
        response = self.client.post(reverse('website:ajax_answer_comment_delete'),\
            {'comment_id': comment_id})
        self.assertContains(response, 'Comment not found.')

    def test_view_post_comment_delete_no_logged_in(self):
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.post(reverse('website:ajax_answer_comment_delete'),\
            {'comment_id': comment_id})
        self.assertContains(response, 'Only moderator can delete.')

    def test_view_post_comment_delete_no_moderator(self):
        self.client.login(username='johndoe2', password='johndoe2')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.post(reverse('website:ajax_answer_comment_delete'),\
            {'comment_id': comment_id})
        self.assertContains(response, 'Only moderator can delete.')

    def test_view_post_comment_delete_with_moderator(self):
        self.client.login(username='johndoe', password='johndoe')
        comment_id = AnswerComment.objects.get(body='TestAnswerComment').id
        response = self.client.post(reverse('website:ajax_answer_comment_delete'),\
            {'comment_id': comment_id})
        self.assertContains(response, 'deleted')

class AjaxNotificationRemoveViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        Notification.objects.create(uid = user.id, qid = question.id)

    def test_view_get_error_at_desired_location(self):
        response = self.client.get('/ajax-notification-remove/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')
    
    def test_view_get_error_accessible_by_name(self):
        response = self.client.get(reverse('website:ajax_notification_remove'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')

    def test_view_post_notification_no_exists(self):
        user_id = User.objects.get(username='johndoe').id
        question_id = Question.objects.get(title='TestQuestion').id
        notification_id = Notification.objects.get(uid=user_id, qid=question_id).id + 1
        response = self.client.post(reverse('website:ajax_notification_remove'),\
            {'notification_id': notification_id})
        self.assertContains(response, 'Notification not found.')

    def test_view_post_unauthorized_user(self):
        user_id = User.objects.get(username='johndoe').id
        question_id = Question.objects.get(title='TestQuestion').id
        notification_id = Notification.objects.get(uid=user_id, qid=question_id).id
        response = self.client.post(reverse('website:ajax_notification_remove'),\
            {'notification_id': notification_id})
        self.assertContains(response, 'Unauthorized user.')
    
    def test_view_post_success(self):
        self.client.login(username='johndoe', password='johndoe')
        user_id = User.objects.get(username='johndoe').id
        question_id = Question.objects.get(title='TestQuestion').id
        notification_id = Notification.objects.get(uid=user_id, qid=question_id).id
        response = self.client.post(reverse('website:ajax_notification_remove'),\
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
        self.assertTemplateUsed(response, 'website/templates/404.html')
    
    def test_view_get_error_accessible_by_name(self):
        response = self.client.get(reverse('website:ajax_keyword_search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/templates/404.html')

    def test_view_post_context_questions(self):
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.post(reverse('website:ajax_keyword_search'),\
            {'key':'Test'})
        self.assertTrue('questions' in response.context)
        self.assertQuerysetEqual(response.context['questions'],\
            ['<Question: {0} - TestCategory -  - TestQuestion - johndoe>'.format(question_id)])

    def test_view_post_correct_template(self):
        question_id = Question.objects.get(title='TestQuestion').id
        response = self.client.post(reverse('website:ajax_keyword_search'),\
            {'key':'Test'})
        self.assertTemplateUsed(response, 'website/templates/ajax-keyword-search.html')

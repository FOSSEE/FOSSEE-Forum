from django.test import TestCase
from django.contrib.auth.models import User
from website.models import Question, Answer, AnswerComment,\
                        FossCategory, Profile, SubFossCategory,\
                        Notification

class FossCategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample test data"""
        FossCategory.objects.create(name="TestCategory", email="category@example.com")

    def test_name_max_length(self):
        category = FossCategory.objects.get(name="TestCategory")
        max_length = category._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    def test_email_max_length(self):
        category = FossCategory.objects.get(name="TestCategory")
        max_length = category._meta.get_field('email').max_length
        self.assertEqual(max_length, 50)
    
    def test_object_name_is_category_name(self):
        category = FossCategory.objects.get(name="TestCategory")
        expected_object_name = category.name
        self.assertEqual(expected_object_name, str(category))

class SubFossCategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample data"""
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        SubFossCategory.objects.create(parent=category, name="TestSubCategory")

    def test_name_max_length(self):
        sub_category = SubFossCategory.objects.get(name="TestSubCategory")
        max_length = sub_category._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_subcat_name(self):
        sub_category = SubFossCategory.objects.get(name="TestSubCategory")
        expected_object_name = sub_category.name
        self.assertEqual(expected_object_name, str(sub_category))

class ProfileModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """Create sample profile"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        Profile.objects.create(user=user, confirmation_code="abdcefgh12345678")

    def test_confirmation_code_max_length(self):
        user = User.objects.get(username="johndoe")
        profile = Profile.objects.get(user=user)
        max_length = profile._meta.get_field('confirmation_code').max_length
        self.assertEqual(max_length, 255)
    
    def test_phone_max_length(self):
        user = User.objects.get(username="johndoe")
        profile = Profile.objects.get(user=user)
        max_length = profile._meta.get_field('phone').max_length
        self.assertEqual(max_length, 20)

    def test_default_phone_is_null(self):
        user = User.objects.get(username="johndoe")
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.phone, None)
    
    def test_default_address_is_null(self):
        user = User.objects.get(username="johndoe")
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.address, None)

class NotificationModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample notification"""
        Notification.objects.create(uid=1, qid=1)

    def test_default_aid(self):
        notification = Notification.objects.get(id=1)
        self.assertEqual(notification.aid, 0)
    
    def test_default_cid(self):
        notification = Notification.objects.get(id=1)
        self.assertEqual(notification.cid, 0)

class QuestionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample question"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        Question.objects.create(user=user, category=category, title="TestQuestion")

    def test_subcat_max_length(self):
        question = Question.objects.get(title="TestQuestion")
        max_length = question._meta.get_field('sub_category').max_length
        self.assertEqual(max_length, 200)

    def test_title_max_length(self):
        question = Question.objects.get(title="TestQuestion")
        max_length = question._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_default_views(self):
        question = Question.objects.get(title="TestQuestion")
        self.assertEqual(question.views, 1)

    def test_default_num_votes(self):
        question = Question.objects.get(title="TestQuestion")
        self.assertEqual(question.num_votes, 0)

    def test_default_spam(self):
        question = Question.objects.get(title="TestQuestion")
        self.assertEqual(question.is_spam, False)

    def test_question_representation(self):
        question = Question.objects.get(title="TestQuestion")
        expected_object_name = '{0} - {1} - {2} - {3} - {4}'.\
                                format(question.id, question.category.name,\
                                question.sub_category, question.title, question.user)
        self.assertEqual(expected_object_name, str(question))

class AnswerModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category, title="TestQuestion")
        Answer.objects.create(question=question, uid=user.id, body="TestAnswer")

    def test_default_num_votes(self):
        answer = Answer.objects.get(body="TestAnswer")
        self.assertEqual(answer.num_votes, 0)

    def test_default_spam(self):
        answer = Answer.objects.get(body="TestAnswer")
        self.assertEqual(answer.is_spam, False)

    def test_answer_representation(self):
        answer = Answer.objects.get(body="TestAnswer")
        expected_object_name = '{0} - {1} - {2}'.format(answer.question.category.name,\
                                answer.question.title, answer.body)
        self.assertEqual(expected_object_name, str(answer))

    def test_user(self):
        answer = Answer.objects.get(body="TestAnswer")
        user = User.objects.get(username="johndoe")
        self.assertEqual(user, answer.user())

class AnswerCommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create sample answer comment"""
        user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
        category = FossCategory.objects.create(name="TestCategory", email="category@example.com")
        question = Question.objects.create(user=user, category=category)
        answer = Answer.objects.create(question=question, uid=user.id)
        AnswerComment.objects.create(answer=answer, uid=user.id, body="TestAnswerComment")

    def test_user(self):
        answer_comment = AnswerComment.objects.get(body="TestAnswerComment")
        user = User.objects.get(username="johndoe")
        self.assertEqual(user, answer_comment.user())
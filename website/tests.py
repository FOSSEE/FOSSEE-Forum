import unittest
from models import FossCategory, Question, QuestionComment, Answer, AnswerComment, Notification, Profile
from django.utils import timezone
from django.core.urlresolvers import reverse

class ProfileTestCases(unittest.TestCase):
    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.profile = Profile.objects.get(pk=1)
        self.user2 = User.objects.get(pk=3)

    def test_user_profile(self):
        """ Test user profile"""
        self.assertEqual(self.user1.username, 'demo_user')
        self.assertEqual(self.profile.user.username, 'demo_user')
        self.assertEqual(int(self.profile.confirmation_code), 1)
        self.assertEqual(int(self.profile.phone), 9876543210)
        self.assertEqual(self.profile.address, 'Mumbai')
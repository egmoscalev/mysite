from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from django.contrib.auth.models import User


import datetime

from .models import Question, Choice

class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        '''
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day and True for questions whose pub_date is within the last day.
        '''
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        '''
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day and True for questions whose pub_date is within the last day.
        '''
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(),False)

    def test_was_published_recently_with_recent_question(self):
        '''
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day and True for questions whose pub_date is within the last day.
        '''
        time = timezone.now() - datetime.timedelta(hours=23,minutes=59,seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(),True)

    def test_has_choices_with_choices(self):
        '''
        has_choices() returns False for questions with no choices
        and True for questions with choices
        '''
        question_with_choices = create_question(question_text="question with choices", days=30)
        create_choices('Choice 1','Choice 2','Choice 3',question=question_with_choices)
        self.assertIs(question_with_choices.has_choices(), True)

    def test_has_choices_with_no_choices(self):
        '''
        has_choices() returns False for questions with no choices
        and True for questions with choices
        '''
        question_with_choices = create_question(question_text="question with no choices", days=30)
        self.assertIs(question_with_choices.has_choices(), False)

    def test_was_published_already_with_future_question(self):
        '''
        was_published_already returns False for questions whose pub_date is set in the future
        and True for questions whose pub_date is set in the past
        '''
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_already(), False)

    def test_was_published_already_with_old_question(self):
        '''
        was_published_already returns False for questions whose pub_date is set in the future
        and True for questions whose pub_date is set in the past
        '''
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_already(),True)

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choices(*choices_text, question):
    for choice_text in choices_text:
        Choice.objects.create(question=question,choice_text=choice_text)

'''
D: question is displayed
P: question pub_date is in the past (question was published already)
C: question has choices
S: user is superuser (admin)

D=PC+S

'''


class QuestionDetailViewTest(TestCase):
    
    def test_past_question_with_choices(self):
        '''
        Questions with a pub_date in the past
        AND with choices are displayed on the
        detail page.
        '''
        question = create_question(question_text="Past question with choices", days=-30)
        create_choices('Choice 1','Choice 2','Choice 3',question=question)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        
        self.assertContains(response, question.question_text)
    
    def test_future_question_with_choices(self):
        '''
        Questions with a pub_date in the future aren't displayed on
        the detail page.
        '''
        question = create_question(question_text="Future question.", days=30)
        create_choices('Choice 1','Choice 2','Choice 3',question=question)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code,404)

    def test_past_question_without_choices(self):
        '''
        Questions without choices aren't displayed on
        the detail page.
        '''
        question = create_question(question_text="Future question.", days=-30)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code,404)

    def test_questions_with_superuser(self):
        '''
        All questions are displayed if the current user is superuser
        '''
        User.objects.create_superuser(username="admin", password="1234")
        self.client.login(username="admin", password="1234")
        question = create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertContains(response, question.question_text)

class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        '''
        If no questions exist, displays the right message
        '''
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question_with_choices(self):
        '''
        Questions with a pub_date in the past
        AND with choices are displayed on the
        index page.
        '''
        question = create_question(question_text="Past question with choices", days=-30)
        create_choices('Choice 1','Choice 2','Choice 3',question=question)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question],
        )
    
    def test_future_question_with_choices(self):
        '''
        Questions with a pub_date in the future aren't displayed on
        the index page.
        '''
        question = create_question(question_text="Future question.", days=30)
        create_choices('Choice 1','Choice 2','Choice 3',question=question)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question_without_choices(self):
        '''
        Questions without choices aren't displayed on
        the index page.
        '''
        create_question(question_text="Future question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_questions_with_superuser(self):
        '''
        All questions are displayed if the current user is superuser
        '''
        User.objects.create_superuser(username="admin", password="1234")
        self.client.login(username="admin", password="1234")

        question = create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question],
        )

class QuestionResultsViewTests(TestCase):

    def test_past_question_with_choices(self):
        '''
        Questions with a pub_date in the past
        AND with choices are displayed on the
        results page.
        '''
        question = create_question(question_text="Past question with choices", days=-30)
        create_choices('Choice 1','Choice 2','Choice 3',question=question)
        response = self.client.get(reverse("polls:results", args=(question.id,)))
        
        self.assertContains(response, question.question_text)
    
    def test_future_question_with_choices(self):
        '''
        Questions with a pub_date in the future aren't displayed on
        the results page.
        '''
        question = create_question(question_text="Future question.", days=30)
        create_choices('Choice 1','Choice 2','Choice 3',question=question)
        response = self.client.get(reverse("polls:results", args=(question.id,)))
        self.assertEqual(response.status_code,404)

    def test_past_question_without_choices(self):
        '''
        Questions without choices aren't displayed on
        the results page.
        '''
        question = create_question(question_text="Future question.", days=-30)
        response = self.client.get(reverse("polls:results", args=(question.id,)))
        self.assertEqual(response.status_code,404)

    def test_questions_with_superuser(self):
        '''
        All questions are displayed if the current user is superuser
        '''
        User.objects.create_superuser(username="admin", password="1234")
        self.client.login(username="admin", password="1234")
        question = create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:results", args=(question.id,)))
        self.assertContains(response, question.question_text)

class QuestionVoteViewTests(TestCase):
    def test_past_question_with_choices(self):
        '''
        Questions with a pub_date in the past
        AND with choices are displayed on the
        vote page.
        '''
        question = create_question(question_text="Past question with choices", days=-30)
        create_choices('Choice 1','Choice 2','Choice 3',question=question)
        response = self.client.get(reverse("polls:vote", args=(question.id,)))
        
        self.assertContains(response, question.question_text)
    
    def test_future_question_with_choices(self):
        '''
        Questions with a pub_date in the future aren't displayed on
        the vote page.
        '''
        question = create_question(question_text="Future question.", days=30)
        create_choices('Choice 1','Choice 2','Choice 3',question=question)
        response = self.client.get(reverse("polls:vote", args=(question.id,)))
        self.assertEqual(response.status_code,404)

    def test_past_question_without_choices(self):
        '''
        Questions without choices aren't displayed on
        the vote page.
        '''
        question = create_question(question_text="Future question.", days=-30)
        response = self.client.get(reverse("polls:vote", args=(question.id,)))
        self.assertEqual(response.status_code,404)

    def test_questions_with_superuser(self):
        '''
        All questions are displayed if the current user is superuser
        '''
        User.objects.create_superuser(username="admin", password="1234")
        self.client.login(username="admin", password="1234")
        question = create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:vote", args=(question.id,)))
        self.assertContains(response, question.question_text)


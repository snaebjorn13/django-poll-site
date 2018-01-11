import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Question

# Create your tests here.
class QuestionModelTests(TestCase):
	def test_was_published_recently_with_future_question(self):
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		self.assertIs(future_question.was_published_recently(), False)

	def test_was_published_recently_with_old_question(self):
		time = timezone.now() - datetime.timedelta(days=1, seconds=1)
		old_question = Question(pub_date=time)
		self.assertIs(old_question.was_published_recently(), False)

	def test_was_published_recently_with_recent_question(self):
		time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
		recent_question = Question(pub_date=time)
		self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)

def get_latest_question_list(response):
	return response.context['latest_question_list']

class QuestionIndexViewTests(TestCase):
	def test_no_questions(self):
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(get_latest_question_list(response), [])

	def test_past_question(self):
		question_text = "Past question."
		create_question(question_text=question_text, days=-30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(get_latest_question_list(response),
			['<Question: %s>' % question_text])

	def test_future_question(self):
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(get_latest_question_list(response), [])

	def test_future_question_and_past_question(self):
		past_qst_text = "Past question."
		create_question(question_text=past_qst_text, days=-30)
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(get_latest_question_list(response),
			['<Question: %s>' % past_qst_text])

	def test_two_past_questions(self):
		past_qst1_text = "Past question 1."
		past_qst2_text = "Past question 2."
		create_question(question_text=past_qst1_text, days=-30)
		create_question(question_text=past_qst2_text, days=-5)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(get_latest_question_list(response),
			['<Question: %s>' % past_qst2_text,
			'<Question: %s>' % past_qst1_text])

class QuestionDetailViewTests(TestCase):
	def test_future_question(self):
		future_question = create_question(question_text='Future question.', days = 5)
		url = reverse('polls:detail', args=(future_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_past_question(self):
		past_question = create_question(question_text='Past question.', days=-5)
		url = reverse('polls:detail', args=(past_question.id,))
		response = self.client.get(url)
		self.assertContains(response, past_question.question_text)

class ResultsDetailViewTests(TestCase):
	def test_future_question(self):
		future_question = create_question(question_text='Future question.', days=5)
		url = reverse('polls:results', args=(future_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_past_question(self):
		past_question = create_question(question_text='Past question.', days=-5)
		url = reverse('polls:results', args=(past_question.id,))
		response = self.client.get(url)
		self.assertContains(response, past_question.question_text)
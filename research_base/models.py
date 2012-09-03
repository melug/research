#!/usr/bin/python
# -*- coding: utf8 -*-
import json

from django.db.models import Count
from django.db import models
from django.contrib.auth.models import User

date_format = '%y/%m/%d %H:%M'

def trim(text, max_size):
    if len(text) < max_size: return text
    return text[:max_size] + '...'

SURVEY_STATE = (
    (1, 'Эхлүүлсэн'),
    (2, 'Дууссан'),
    (3, 'Засварт'),
    (4, 'Устгасан'),
)

class Survey(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    state = models.IntegerField(choices=SURVEY_STATE)
    added_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return  trim(self.title, 50)

    def count_responders(self):
        return self.surveyuser_set.count()

    def count_partial_responders(self):
        return self.surveyuser_set.filter(finished=False).count()

class Page(models.Model):
    title = models.CharField(max_length=255)
    survey = models.ForeignKey(Survey)

    def __unicode__(self):
        return self.survey.title + ' - ' + self.title
        
    def questions(self):
        return self.question_set.filter(parent_question__isnull=True)

class SurveyUser(models.Model):
    firstname = models.CharField(max_length=255, blank=True)
    finished = models.BooleanField(default=0)
    lastname = models.CharField(max_length=255, blank=True)
    session_key = models.CharField(max_length=255, blank=True)
    survey = models.ForeignKey(Survey)
    user_id = models.CharField(max_length=255)

    def __unicode__(self):
        return self.firstname or self.session_key or self.user_id

QUESTION_TYPE = (
    (1, 'Нэгийг сонгох'),
    (2, 'Олныг сонгох'),
    (3, 'Тоо оруулах'),
    (4, 'Текст оруулах'),
    (5, 'Хүснэгтэн хэлбэрээр нэгийг сонгох'),
)

class Question(models.Model):
    question = models.TextField()
    page = models.ForeignKey(Page)
    question_type = models.IntegerField(choices=QUESTION_TYPE)
    parent_question = models.ForeignKey('self', null=True, related_name='subquestions') # used for table of radio

    def __unicode__(self):
        return trim(self.question, 100)

    def count_answers(self):
        if self.question_type in (1, 2):
            return [ (at.value, at.answer__count) for at in self.answertype_set.annotate(Count('answer')) ]

class AnswerType(models.Model):
    value = models.CharField(max_length=255)
    question = models.ForeignKey(Question)

    def __unicode__(self):
        return self.value

class Answer(models.Model):
    survey_user = models.ForeignKey(SurveyUser)
    survey = models.ForeignKey(Survey)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(AnswerType, null=True)
    answer_text = models.TextField(blank=True)
    
    def __unicode__(self):
        if self.answer:
            real_answer = self.answer.value
        else:
            real_answer = self.answer_text
        return self.question.question + ' : ' + real_answer


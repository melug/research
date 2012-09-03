#!/usr/bin/python
# -*- coding: utf8 -*-
from django import forms
from research_base.models import Survey, Page, Question, Answer, AnswerType

class AnswerForm(forms.Form):
    select_one_answers = forms.ChoiceField(required=False, widget=forms.RadioSelect(), label='')
    select_multiple_answers = forms.MultipleChoiceField(required=False, label='')
    text_input = forms.CharField(required=False, label='')
    number_input = forms.IntegerField(required=False, label='')

    def __init__(self, question, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.question = question
        field_name = None
        if question.question_type == 1:
            field_name = 'select_one_answers'
        elif question.question_type == 2:
            field_name = 'select_multiple_answers'
        if question.question_type in (1, 2):
            self.fields[field_name].choices = [ (a.id, a.value) for a in question.answertype_set.all() ]
            self.fields[field_name].label = self.question.question
            if question.question_type == 1:
                self.fields[field_name].widget = forms.RadioSelect(choices=self.fields[field_name].choices)
    
    def clean_select_one_answers(self):
        if not self.cleaned_data['select_one_answers'] and self.question.question_type == 1:
            raise forms.ValidationError('Хариултаа сонгоно уу')
        return self.cleaned_data['select_one_answers']

    def clean_select_multiple_answers(self):
        if not self.cleaned_data['select_multiple_answers'] and self.question.question_type == 2:
            raise forms.ValidationError('Хариултаа сонгоно уу')
        return self.cleaned_data['select_multiple_answers']

    def clean_number_input(self):
        if not self.cleaned_data['number_input'] and self.question.question_type == 3:
            raise forms.ValidationError('Тоо оруулна уу')
        return self.cleaned_data['number_input']

    def clean_text_input(self):
        if not self.cleaned_data['text_input'] and self.question.question_type == 4:
            raise forms.ValidationError('Текст оруулна уу')
        return self.cleaned_data['text_input']

    def save_answers(self, survey_user):
        if self.question.question_type == 1:
            answer_type = AnswerType.objects.get(pk=self.cleaned_data['select_one_answers'])
            Answer.objects.create(survey_user=survey_user, survey=survey_user.survey,
                question=self.question, answer=answer_type, answer_text='')
        elif self.question.question_type == 2:
            for answer_type_id in self.cleaned_data['select_multiple_answers']:
                answer_type = AnswerType.objects.get(pk=answer_type_id)
                Answer.objects.create(survey_user=survey_user, survey=survey_user.survey,
                    question=self.question, answer=answer_type, answer_text='')
        elif self.question.question_type == 3:
            Answer.objects.create(survey_user=survey_user, survey=survey_user.survey,
                question=self.question, answer=None, answer_text=self.cleaned_data['number_input'])
        elif self.question.question_type == 4:
            Answer.objects.create(survey_user=survey_user, survey=survey_user.survey,
                question=self.question, answer=None, answer_text=self.cleaned_data['text_input'])
        else:
            #print 'I dont care other types'
            pass

def get_answer_forms(questions, data=None):
    return [ AnswerForm(q, data, prefix=q.id) for q in questions ]

###################################
class SurveyForm(forms.ModelForm):
    
    class Meta:
        model = Survey
        exclude = ('user', 'state')

class PageForm(forms.ModelForm):
    
    class Meta:
        model = Page
        exclude = ('survey',)

class QuestionForm(forms.ModelForm):
    question = forms.CharField(widget=forms.Textarea(attrs={'class':'input-xlarge', 'rows':'5'}))
    questions = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'input-xlarge', 'rows':'5'}))
    answers = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'input-xlarge', 'rows':'5'}))
    class Meta:
        model = Question
        exclude = ('page', 'parent_question',)

SURVEY_STATE = (
    (0, 'Бүгд'),
    ('Төлвөөр нь шүүх', (
        (1, 'Эхлүүлсэн'),
        (2, 'Дууссан'),
        (3, 'Засварт'),
        (4, 'Устгасан'),
    ),)
)

class SurveyFilterForm(forms.Form):
    state = forms.ChoiceField(choices=SURVEY_STATE)

class PublishSurveyForm(forms.ModelForm):
    
    class Meta:
        model = Survey
        fields = ('state',)


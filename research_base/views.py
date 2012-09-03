from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView, View
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from sendfile import sendfile

from research_base.forms import AnswerForm, get_answer_forms, SurveyForm, Survey, PageForm, QuestionForm, SurveyFilterForm, PublishSurveyForm
from research_base.models import Page, Survey, AnswerType, Question, SurveyUser, Answer

class RedirectView(View):
    redirect_url = ''

    def get_redirect_url(self):
        return self.redirect_url

    def get(self, request, **kwargs):
        return redirect(self.get_redirect_url())

class HomeRedirect(RedirectView):
    
    def get_redirect_url(self):
        return reverse('account_login')

class SurveyList(ListView):
    
    def get_context_data(self, *args, **kwargs):
        data = super(SurveyList, self).get_context_data(*args, **kwargs)
        data.update({
            'survey_count': self.get_queryset().count(),
            'survey_form': SurveyForm(),
            'survey_filterform' : SurveyFilterForm(self.request.GET),
            'all_surveys': Survey.objects.filter(user=self.request.user),
        })
        return data
    
    def get_queryset(self):
        filter_survey = SurveyFilterForm(self.request.GET)
        surveys = Survey.objects.filter(user=self.request.user)
        if filter_survey.is_valid():
            state = int(filter_survey.cleaned_data['state'])
            if state != 0: 
                surveys = surveys.filter(state=filter_survey.cleaned_data['state'])
            else:
                surveys = surveys.exclude(state=4)
        else:
            surveys = surveys.exclude(state=4)
        return surveys.order_by('-added_date')

class UpdateSurvey(UpdateView):
    form_class = SurveyForm
    template_name = 'research_base/survey_settings.html'

    def get_context_data(self, **kwargs):
        data = super(UpdateSurvey, self).get_context_data(**kwargs)
        data['survey'] = self.get_object()
        return data

    def get_queryset(self):
        return Survey.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('update-survey', kwargs={'pk': self.object.id})

class SurveyDetail(DetailView):
    
    def get_queryset(self):
        return Survey.objects.filter(user=self.request.user)

class CreateSurvey(CreateView):
    form_class = SurveyForm
    template_name = 'research_base/survey_form.html'

    def get_success_url(self):
        return reverse('add-page', kwargs={'survey_id': self.object.id})

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():    
            self.object = form.save(commit=False)
            self.object.user = request.user
            self.object.state = 3
            self.object.save()
            page = Page.objects.create(title='First page', survey=self.object)
            return HttpResponseRedirect(self.get_success_url())
        else:
            print 'form is not valid', form.errors
            return self.form_invalid(form) 

class DeleteSurvey(DeleteView):
    
    def get_queryset(self):
        return Survey.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse('survey-list')

class AddPage(CreateView):
    form_class = PageForm
    template_name = 'research_base/page_form.html'

    def get_context_data(self, **kwargs):
        data = super(AddPage, self).get_context_data(**kwargs)
        data['survey'] = Survey.objects.get(id=self.kwargs['survey_id'])
        data['question_form'] = QuestionForm(initial={ 'question_type': 1 })
        data['update_form'] = PageForm()
        return data

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():    
            self.object = form.save(commit=False)
            self.object.survey = Survey.objects.get(id=kwargs['survey_id'])
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form) 

    def get_success_url(self):
        return reverse('add-page', kwargs={'survey_id': self.object.survey.id})

class PageDetail(DetailView):
    
    def get_queryset(self):
        return Page.objects.all()

class UpdatePage(UpdateView):
    form_class = PageForm

    def get_queryset(self):
        return Page.objects.filter(survey__user=self.request.user)
        
    def get_success_url(self):
        return reverse('add-page', kwargs={'survey_id': self.object.survey.id})

class DeletePage(DeleteView):
    
    def get_queryset(self):
        return Page.objects.all()
    
    def get_success_url(self):
        return reverse('survey-detail', kwargs={ 'pk': self.object.survey_template.id })
    
class AddQuestion(CreateView):
    form_class = QuestionForm
    template_name = 'research_base/question_form.html'

    def get_context_data(self, **kwargs):
        data = super(AddQuestion, self).get_context_data(**kwargs)
        data['page'] = Page.objects.get(id=self.kwargs['page_id'])
        return data

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():    
            self.object = form.save(commit=False)
            self.object.page = Page.objects.get(id=kwargs['page_id'])
            self.object.save()
            if self.object.question_type == 1 or self.object.question_type == 2:
                for answer in form.cleaned_data['answers'].splitlines():
                    AnswerType.objects.create(value=answer, question=self.object)
            if self.object.question_type == 5:
                for question in form.cleaned_data['questions'].splitlines():
                    q = Question.objects.create(question=question, page=self.object.page, parent_question=self.object, question_type=1)
                    for answer in form.cleaned_data['answers'].splitlines():
                        AnswerType.objects.create(value=answer, question=q)
            return HttpResponseRedirect(self.get_success_url() + '#question' + str(self.object.id))
        else:
            return self.form_invalid(form) 

    def get_success_url(self):
        return reverse('add-page', kwargs={ 'survey_id': self.object.page.survey.id })

class UpdateQuestion(UpdateView):
    form_class = QuestionForm
    template_name = 'research_base/question_update.html'

    def get_queryset(self):
        return Question.objects.all()

    def get_context_data(self, **kwargs):
        data = super(UpdateQuestion, self).get_context_data(**kwargs)
        data['page'] = self.get_object().page
        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():    
            self.object = form.save(commit=False)
            self.object.page = self.get_object().page
            self.object.save()
            self.object.answertype_set.all().delete()
            answer_counter = 0
            while True:
                param_name = 'answer' + str(answer_counter)
                if param_name in request.POST:
                    value = request.POST[param_name]
                    AnswerType.objects.create(value=value, question=self.object)
                else:
                    break
                answer_counter += 1
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form) 

    def get_success_url(self):
        return reverse('page-detail', kwargs={ 'pk': self.get_object().page.id })

class DeleteQuestion(DeleteView):

    def get_queryset(self):
        return Question.objects.filter(page__survey__user=self.request.user)

    def get_success_url(self):
        return reverse('add-page', kwargs={ 'survey_id': self.object.page.survey.id })

class PublishSurvey(UpdateView):
    form_class = PublishSurveyForm
    template_name = 'research_base/launch_survey.html'
    
    def get_context_data(self, **kwargs):
        data = super(PublishSurvey, self).get_context_data(**kwargs)
        data['survey'] = self.get_object()
        return data
        
    def get_queryset(self):
        return Survey.objects.filter(user=self.request.user)
        
    def get_success_url(self):
        return reverse('launch-survey', kwargs={ 'pk': self.object.id })

class SurveyReport(DetailView):
    template_name = 'research_base/survey_report.html'

    def get_queryset(self):
        return Survey.objects.filter(user=self.request.user)

class ExportSurvey(DetailView):
    template_name = 'research_base/survey_export.html'

    def get_queryset(self):
        return Survey.objects.filter(user=self.request.user)

    def post(self, request, **kwargs):
        file_name = '/tmp/a.xls'
        export_survey(self.get_object(), file_name)
        return sendfile(request, file_name, attachment=True, attachment_filename='research export.xls')

def start_survey(request, survey_id):
    if request.method == 'GET':
        return render_to_response('survey_login.html', context_instance=RequestContext(request))
    else:
        survey = get_object_or_404(Survey.objects.filter(state=1), pk=survey_id)
        user_id = request.POST.get('user_id', '')
        if not user_id:
            return render_to_response('errors.html', { 'code': 1 }, context_instance=RequestContext(request))
        survey_user, is_created = SurveyUser.objects.get_or_create(user_id=user_id, survey=survey)
        if survey_user.finished:
            return render_to_response('errors.html', { 'code': 2 }, context_instance=RequestContext(request))
        if not is_created:
            Answer.objects.filter(survey_user=survey_user).delete()
        request.session['surveyuser_id'] = survey_user.id
        return redirect(reverse('take-survey', kwargs={ 'survey_id': survey.id, 'page_id': 0 }))

def counter():
    i = 1
    while True:
        yield i
        i += 1

def take_survey(request, survey_id, page_id):
    page_id = int(page_id)
    survey = get_object_or_404(Survey.objects.filter(state=1), pk=survey_id)
    try:
        survey_user = SurveyUser.objects.get(pk=request.session.get('surveyuser_id', -1))
    except SurveyUser.DoesNotExist:
        return redirect(reverse('start-survey', kwargs={ 'survey_id': survey.id }))
    page = survey.page_set.all()[page_id]
    if request.method == 'GET':
        return render_to_response('form.html', {
            'forms': get_answer_forms(page.question_set.all()),
            'page': page,
            'survey': survey,
            'counter': counter(),
        }, context_instance=RequestContext(request))
    else:
        forms = get_answer_forms(page.question_set.all(), request.POST)
        all_forms_valid = True
        for form in forms:
            if not form.is_valid():
                all_forms_valid = False
        if all_forms_valid:
            for form in forms:
                form.save_answers(survey_user)
        else:
            return render_to_response('form.html', {
                'forms': forms,
                'page': page,
                'survey': survey,
                'counter': counter(),
            }, context_instance=RequestContext(request))
        try:
            next_page = survey.page_set.all()[page_id+1]
            return redirect(reverse('take-survey', kwargs={ 'survey_id': survey.id, 'page_id': page_id+1 }))
        except Exception as e:
            print e
        return redirect(reverse('finish-survey'))

def finish_survey(request):
    try:
        survey_user = SurveyUser.objects.get(pk=request.session.get('surveyuser_id', -1))
        survey_user.finished = True
        survey_user.save()
    except SurveyUser.DoesNotExist:
        return redirect('/')
    return redirect(reverse('thank-you'))

def export_survey(survey, file_name):
    from xlwt import Workbook
    wb = Workbook()
    sheet = wb.add_sheet('Sheet 1')
    row = 0
    for page in survey.page_set.all():
        for question in page.questions():
            sheet.write_merge(row, row, 0, 7, question.question)
            row += 1
            if question.question_type in (1, 2):
                for value, count in question.count_answers():
                    sheet.write(row, 1, value)
                    sheet.write(row, 2, '(%d)'%count)
                    row += 1
            elif question.question_type == 5:
                for subquestion in question.subquestions.all():
                    sheet.write_merge(row, row, 0, 7, subquestion.question)
                    row += 1
                    for value, count in subquestion.count_answers():
                        sheet.write(row, 1, value)
                        sheet.write(row, 2, '(%d)'%count)
                        row += 1
    wb.save(file_name)


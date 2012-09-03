from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from research_base.views import (
    SurveyDetail, CreateSurvey,  PublishSurvey, UpdateSurvey, ExportSurvey,
    CreateSurvey, SurveyList, AddPage, DeleteSurvey, SurveyReport,
    PageDetail, DeletePage, UpdatePage, HomeRedirect,
    AddQuestion, UpdateQuestion, DeleteQuestion)

urlpatterns = patterns("research_base.views",
    url(r"^$", HomeRedirect.as_view()),
    url(r"^surveys/$", login_required(
            SurveyList.as_view()), name="survey-list"),
    url(r"^surveys/(?P<pk>\d+)/$", login_required(
            SurveyDetail.as_view()), name="survey-detail"),
    url(r"^surveys/(?P<pk>\d+)/launch/$", login_required(
            PublishSurvey.as_view()), name="launch-survey"),
    url(r"^surveys/(?P<pk>\d+)/export/$", login_required(
            ExportSurvey.as_view()), name="export-survey"),
    url(r"^surveys/(?P<pk>\d+)/delete/$", login_required(
            DeleteSurvey.as_view()), name="delete-survey"),
    url(r"^surveys/create/$", login_required(
            CreateSurvey.as_view()), name="create-survey"),
    url(r"^survey/(?P<pk>\d+)/settings/$", login_required(
            UpdateSurvey.as_view()), name="update-survey"),
    url(r"^survey/(?P<pk>\d+)/report/$", login_required(
            SurveyReport.as_view()), name="survey-report"),
    url(r"^survey/(?P<survey_id>\d+)/add_page/$", login_required(
            AddPage.as_view()), name="add-page"),
    url(r"^pages/(?P<pk>\d+)/$", login_required(
            PageDetail.as_view()), name="page-detail"),
    url(r"^pages/(?P<pk>\d+)/delete/$", login_required(
            DeletePage.as_view()), name="delete-page"),
    url(r"^pages/(?P<pk>\d+)/update/$", login_required(
            UpdatePage.as_view()), name="update-page"),
    url(r"^pages/(?P<page_id>\d+)/add_question/$", login_required(
            AddQuestion.as_view()), name="add-question"),
    url(r"^questions/(?P<pk>\d+)/update/$", login_required(
            UpdateQuestion.as_view()), name="update-question"),
    url(r"^questions/delete/(?P<pk>\d+)/$", login_required(
            DeleteQuestion.as_view()), name="delete-question"),
    url(r"^survey/(?P<survey_id>\d+)/take/$", 'start_survey', name="start-survey"),
    url(r"^survey/(?P<survey_id>\d+)/take/(?P<page_id>\d+)/$", 'take_survey', name="take-survey"),
    url(r"^survey/finish/$", 'finish_survey', name="finish-survey"),
    url(r"^thankyou/$", direct_to_template, { 'template': 'thankyou.html' }, name="thank-you"),
)


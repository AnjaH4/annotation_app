from django.urls import path
from surveyapp.views import introPage, familiarizationPage, helpPage, exampleTask, \
     mainQuPage, survey_complete

urlpatterns = [
    path('intro', introPage, name='intro'),
    path('exampleTask', exampleTask, name='exampleTask'),
    path('introHelp', helpPage, name='introHelp'),
    path('introFamiliarization', familiarizationPage, name='introFamiliarization'),
    path('main', mainQuPage, name='main1'),
    path('submit_answer', mainQuPage, name='submit_answer'),
    path('survey_complete', survey_complete, name='survey_complete')
]

handler500 = 'surveyapp.views.handler500'

from django.urls import path
from . import views  # Using a relative import is best practice here

urlpatterns = [
    path('intro/', views.introPage, name='intro'),
    path('exampleTask/', views.exampleTask, name='exampleTask'),
    path('introHelp/', views.helpPage, name='introHelp'),
    path('introFamiliarization/', views.familiarizationPage, name='introFamiliarization'),
    path('main/', views.mainQuPage, name='main1'),
    path('submit_answer/', views.mainQuPage, name='submit_answer'),
    path('survey_complete/', views.survey_complete, name='survey_complete'),
]

handler500 = 'surveyapp.views.handler500'

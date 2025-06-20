from django.contrib import admin
from django.urls import path, include
from django.urls import re_path as url
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', lambda r: HttpResponseRedirect('surveyapp/intro')),
    path('surveyapp/', include('surveyapp.urls')),
    path('i18n/setlang/', set_language, name='set_language'),
]

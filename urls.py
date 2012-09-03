from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='account_login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', { 'next_page' : '/accounts/login/' }, name='account_logout'),
    url(r"^", include('research_base.urls')),
    url(r"^", include('htmleditor.urls')),
    url(r"^admin/", include(admin.site.urls)),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )

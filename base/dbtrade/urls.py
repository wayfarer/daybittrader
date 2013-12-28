from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'dbtrade.apps.trader.views.home', name='home'),
    url(r'^logout/$', 'dbtrade.apps.trader.views.logout', name='logout'),
    url(r'^historical/$', 'dbtrade.apps.trader.views.historical', name='historical'),
    url(r'^about/$', 'dbtrade.apps.trader.views.about', name='about'),
    url(r'^notification/$', 'dbtrade.apps.trader.views.notification'),
    url(r'^notification/(?P<uuid>[-\w]+)/$', 'dbtrade.apps.trader.views.notification'),
    
    url(r'^_callback/_access/_$', 'dbtrade.apps.trader.callback.access_fee'),
    
    url(r'^admin/', include(admin.site.urls)),
)

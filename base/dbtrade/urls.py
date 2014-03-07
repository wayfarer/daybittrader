from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'dbtrade.apps.trader.views.home', name='home'),
    url(r'^logout/$', 'dbtrade.apps.trader.views.logout', name='logout'),
    url(r'^historical/$', 'dbtrade.apps.trader.views.historical', name='historical'),
    url(r'^about/$', 'dbtrade.apps.trader.views.about', name='about'),
    url(r'^notification/$', 'dbtrade.apps.trader.views.notification', name='notification'),
    url(r'^notification/(?P<uuid>[-\w]+)/$', 'dbtrade.apps.trader.views.notification', name='notification_detail'),
    
    url(r'^login/coinbase/$', 'dbtrade.apps.trader.views.login_coinbase', name='login_coinbase'),
    url(r'^connect/coinbase/$', 'dbtrade.apps.trader.callback.connect_coinbase'),
    url(r'^connect/coinbase/callback/$', 'dbtrade.apps.trader.callback.connect_coinbase_callback'),
    
    url(r'^_callback/_access/_$', 'dbtrade.apps.trader.callback.access_fee'),
    
    url(r'^trade/', include('dbtrade.apps.trader.trade.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
)

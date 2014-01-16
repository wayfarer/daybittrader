from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'dbtrade.apps.trader.trade.views.home', name='trade_home'),
    url(r'^login/$', 'dbtrade.apps.trader.trade.views.login', name='trade_login'),
    url(r'^buy/$', 'dbtrade.apps.trader.trade.views.buy', name='trade_buy'),
    url(r'^sell/$', 'dbtrade.apps.trader.trade.views.sell', name='trade_sell'),
)

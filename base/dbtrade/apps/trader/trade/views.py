from datetime import timedelta, datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from dbtrade.utils.utils import get_user_cb_api
from dbtrade.apps.trader.models import TradeOrder, TickerHistory


@login_required(login_url='/#login-form')
def home(request):
    template = 'trade_home.html'
    
    env = {}
    return render_to_response(template, RequestContext(request, env))


@login_required(login_url='/#login-form')
def login(request):
    template = 'trade_login.html'
    CB_API = get_user_cb_api(request.user)
    if CB_API != None:
        return HttpResponseRedirect('/trade/')
    
    ref = request.GET.get('ref', '/trade/')
    env = {'ref': ref}
    return render_to_response(template, RequestContext(request, env))


DELTA_TYPE_CHOICES = (('hours', 'Hours'), ('days', 'Days'), ('weeks', 'Weeks'))

class TradeForm(forms.ModelForm):
    expires = forms.IntegerField(label='Trade Expires In')
    expires_type = forms.ChoiceField(widget=forms.RadioSelect, choices=DELTA_TYPE_CHOICES)
    
    class Meta:
        model = TradeOrder
        fields = ['price_point', 'btc_amount']
        
    def save(self, *args, **kwargs):
        deltakwargs = {self.cleaned_data['expires_type']: self.cleaned_data['expires']}
        this_timedelta = timedelta(**deltakwargs)
        self.instance.date_expire = datetime.utcnow() + this_timedelta
        super(TradeForm, self).save(*args, **kwargs)


def trade(request, trade_type):
    template = 'trade_order.html'
    CB_API = get_user_cb_api(request.user)
    if CB_API == None:
        return HttpResponseRedirect('/trade/login/?ref=/trade/%s/' % trade_type.lower())
    
    trade = None
    if request.method == 'POST':
        form = TradeForm(request.POST)
    else:
        form = TradeForm(initial={'expires': 2, 'expires_type': 'days'})
        
    #: TODO: probably other logic here
        
    if request.method == 'POST':
        if form.is_valid():
            form.instance.type = trade_type
            form.instance.user = request.user
            trade = form.save()
            return HttpResponseRedirect('/trade/%s/' % trade_type.lower())
    
    submit_text_dict = {
                        'BUY': 'Create Purchase Order',
                        'SELL': 'Create Sell Order'
                        }
    heading_text_dict = {
                         'BUY': 'Buy Bitcoins',
                         'SELL': 'Sell Bitcoins'
                         }
    current_ticker = TickerHistory.objects.all().order_by('id').reverse()[:1][0]
    current_price_dict = {
                          'BUY': current_ticker.cb_buy_value,
                          'SELL': current_ticker.cb_sell_value
                          }
    
    current_trades = TradeOrder.objects.filter(user=request.user, active=True)
    trades_data = []
    for trade in current_trades:
        trade_data = {
                      'type': trade.type,
                      'price_point': trade.price_point,
                      'btc_amount': trade.btc_amount,
                      'cost': trade.btc_amount * trade.price_point,
                      'expired': trade.date_expire > datetime.utcnow()
                      }
        trades_data.append(trade_data)
    
    env = {
           'heading': heading_text_dict[trade_type],
           'submit_text': submit_text_dict[trade_type],
           'form': form,
           'trade': trade,
           'trade_type': trade_type,
           'trade_type_lower': trade_type.lower(),
           'cb_balance': CB_API.balance,
           'current_price': current_price_dict[trade_type],
           'trades': trades_data
           }
    return render_to_response(template, RequestContext(request, env))


@login_required(login_url='/#login-form')
def buy(request):
    return trade(request, 'BUY')


@login_required(login_url='/#login-form')
def sell(request):
    return trade(request, 'SELL')


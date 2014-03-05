from datetime import timedelta, datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from dbtrade.utils.utils import get_user_cb_api
from dbtrade.apps.trader.models import TradeOrder, TickerHistory


def get_recent_trades(user):
    return TradeOrder.objects.filter(completion_status='SUCCESS', user=user).order_by('id').reverse()[:10]


@login_required(login_url='/#login-form')
def home(request):
    template = 'trade_home.html'
    
    ticker = TickerHistory.objects.exclude(bs_last=None).order_by('id').reverse()[:1][0]
    
    env = {
           'bitstamp_price': ticker.bs_last,
           'heading': 'Latest Bitstamp Trades'
           }
    return render_to_response(template, RequestContext(request, env))


@login_required(login_url='/#login-form')
def login(request):
    template = 'trade_login.html'
    CB_API = get_user_cb_api(request.user)
    if CB_API != None:
        return HttpResponseRedirect('/trade/')
    
    ref = request.GET.get('ref', '/trade/')
    env = {'ref': ref, 'heading': 'Log in with Coinbase'}
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
    authorized = CB_API != None
    if authorized:
        try:
            cb_balance = CB_API.balance
        except ValueError:
            authorized = False
    
    if not authorized:
        return HttpResponseRedirect('/trade/login/?ref=/trade/%s/' % trade_type.lower())
    
    remove_uuid = request.GET.get('remove', '')
    if remove_uuid:
        try:
            trade = TradeOrder.objects.get(uuid=remove_uuid)
        except TradeOrder.DoesNotExist:
            print 'Invalid UUID selected for removal.'
        else:
            trade.active = False
            trade.save()
        return HttpResponseRedirect('/trade/%s/' % trade_type.lower().replace('_', ''))
    
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
            return HttpResponseRedirect('/trade/%s/' % trade_type.lower().replace('_', ''))
    
    submit_text_dict = {
                        'BUY': 'Create Purchase Order',
                        'SELL': 'Create Sell Order',
                        'STOP_LOSS': 'Create Stop Loss'
                        }
    heading_text_dict = {
                         'BUY': 'Buy Bitcoins',
                         'SELL': 'Sell Bitcoins',
                         'STOP_LOSS': 'Stop Loss'
                         }
    current_ticker = TickerHistory.objects.all().order_by('id').reverse()[:1][0]
    current_price_dict = {
                          'BUY': current_ticker.cb_buy_value,
                          'SELL': current_ticker.cb_sell_value,
                          'STOP_LOSS': current_ticker.cb_sell_value
                          }
    
    current_trades = TradeOrder.objects.filter(user=request.user, active=True)
    trades_data = []
    for trade in current_trades:
        trade_data = {
                      'type': trade.type,
                      'uuid': trade.uuid,
                      'parent_trade': trade.parent_trade,
                      'price_point': '%.2f' % trade.price_point,
                      'btc_amount': float(trade.btc_amount),#:converting to float strips zeros from right side
                      'cost': '%.2f' % (trade.btc_amount * trade.price_point),
                      'expired': trade.date_expire < now()
                      }
        trades_data.append(trade_data)
    
    env = {
           'heading': heading_text_dict[trade_type],
           'submit_text': submit_text_dict[trade_type],
           'form': form,
           'trade': trade,
           'trade_type': trade_type,
           'trade_type_lower': trade_type.lower().replace('_', ' '),
           'cb_balance': cb_balance,
           'current_price': '%.2f' % current_price_dict[trade_type],
           'bitstamp_price': '%.2f' % current_ticker.bs_last,
           'trades': trades_data,
           'recent_trades': get_recent_trades(request.user)
           }
    return render_to_response(template, RequestContext(request, env))


@login_required(login_url='/#login-form')
def buy(request):
    return trade(request, 'BUY')


@login_required(login_url='/#login-form')
def sell(request):
    return trade(request, 'SELL')


@login_required(login_url='/#login-form')
def stoploss(request):
    return trade(request, 'STOP_LOSS')


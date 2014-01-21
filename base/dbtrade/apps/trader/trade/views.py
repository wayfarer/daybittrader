from datetime import timedelta, datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from dbtrade.utils.utils import get_user_cb_api
from dbtrade.apps.trader.models import TradeOrder


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
    expires = forms.IntegerField()
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
            trade = form.save()
            return HttpResponseRedirect('/trade/%s/' % trade_type.lower())
    
    env = {
           'submit_text': 'Create Purchase Order',
           'form': form,
           'trade': trade,
           'trade_type': trade_type
           }
    return render_to_response(template, RequestContext(request, env))


@login_required(login_url='/#login-form')
def buy(request):
    return trade(request, 'BUY')


@login_required(login_url='/#login-form')
def sell(request):
    return trade(request, 'SELL')


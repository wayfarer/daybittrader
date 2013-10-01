from datetime import timedelta
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
#from django import forms
#from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as auth_login, logout as auth_logout

from dbtrade.apps.trader.models import TickerHistory


def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/historical/')
    env={}
    return auth_login(request, template_name='home.html', extra_context=env)


def logout(request):
    return auth_logout(request, next_page="/")


@login_required
def historical(request):
    
    days_limit = 15
    
    ticker_queryset = TickerHistory.objects.filter(id__gte=settings.CB_STARTING_ID).exclude(cb_buy_value=None)
    ticker_queryset = ticker_queryset.order_by('date_added').reverse()
    
    ticker_data = []
    last_date = None
    total_dates = 0
    for ticker in ticker_queryset:
        current_date = str(ticker.date_added).split(' ')[0]
        if current_date == last_date:
            continue
        total_dates += 1
        last_date = current_date
        data = {
                'id': ticker.id,
                'date': ticker.date_added,
                'sell_price': ticker.sell_value * 50,
                'buy_price': ticker.cb_buy_value_50,
                'profit': (ticker.sell_value * 50) - ticker.cb_buy_value_50
                }
        ticker_data.append(data)
        if total_dates == days_limit:
            break
        
    ticker_data.reverse()
    
    ticker_data = {
                   'total': len(ticker_data),
                   'data': ticker_data
                   }
    
    #return HttpResponse(str(ticker_data))
    
    today = datetime.today()
    today_baseline = datetime(today.year, today.month, today.day)
    daily_ticker_queryset = TickerHistory.objects.filter(id__gte=settings.CB_STARTING_ID,
                                                         date_added__gte=today_baseline).exclude(cb_buy_value=None)
    daily_ticker_queryset = daily_ticker_queryset.order_by('date_added').reverse()
    
    daily_ticker_data = []

    for ticker in daily_ticker_queryset:
        data = {
                'id': ticker.id,
                'date': ticker.date_added,
                'sell_price': ticker.sell_value * 50,
                'buy_price': ticker.cb_buy_value_50,
                'profit': (ticker.sell_value * 50) - ticker.cb_buy_value_50
                }
        daily_ticker_data.append(data)
        
    daily_ticker_data.reverse()
        
    daily_ticker_data = {
                         'total': len(daily_ticker_data),
                         'data': daily_ticker_data
                         }
    
    env = {
           'ticker_data': ticker_data,
           'daily_ticker_data': daily_ticker_data
           }
    return render_to_response('historical.html', RequestContext(request, env))

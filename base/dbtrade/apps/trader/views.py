from datetime import timedelta
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import forms
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


fee_defaults = {
                'business_days_delay': 2,
                'foreign_wire_fee': Decimal('20.5'),
                'domestic_wire_fee': Decimal('45'),
                'fee_schedule': Decimal('0.6')
                }


class FeeSelector(forms.Form):
    business_days_delay = forms.IntegerField(initial=fee_defaults['business_days_delay'])
    foreign_wire_fee = forms.DecimalField(initial=fee_defaults['foreign_wire_fee'])
    domestic_wire_fee = forms.DecimalField(initial=fee_defaults['domestic_wire_fee'])
    fee_schedule = forms.DecimalField(initial=fee_defaults['fee_schedule'])
    
    
def bus_days_ago(from_date, days_ago):
    if not days_ago:
        return from_date
    true_business_days_delay = 0
    weekday_count = 0
    weekends = [5, 6]
    while True:
        true_business_days_delay += 1
        weekday_test_day = from_date - timedelta(days=true_business_days_delay)
        if weekday_test_day.weekday() not in weekends:
            weekday_count += 1
            if weekday_count == days_ago:
                break
            
    return from_date - timedelta(days=true_business_days_delay)


@login_required
def historical(request):
    
    fields_set = False
    for field in fee_defaults:
        if field in request.GET:
            fields_set = True
    
    business_days_delay = fee_defaults['business_days_delay']
    foreign_wire_fee = fee_defaults['foreign_wire_fee']
    domestic_wire_fee = fee_defaults['domestic_wire_fee']
    fee_schedule = fee_defaults['fee_schedule']
            
    if fields_set:
        form = FeeSelector(request.GET)
    else:
        form = FeeSelector()
    
    if form.is_valid():
        cleaned_data = form.clean()
        business_days_delay = cleaned_data['business_days_delay']
        foreign_wire_fee = cleaned_data['foreign_wire_fee']
        domestic_wire_fee = cleaned_data['domestic_wire_fee']
        fee_schedule = cleaned_data['fee_schedule']
        
    fee_schedule_multiplier = (Decimal('100') - Decimal(str(fee_schedule))) / Decimal('100')
    
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
        sell_price = Decimal(str(((ticker.sell_value * 50) - foreign_wire_fee - domestic_wire_fee)))
        sell_price *= fee_schedule_multiplier
        
        days_ago_limit = bus_days_ago(ticker.date_added, business_days_delay)
        ticker_business_days_ago = TickerHistory.objects.filter(
                                    date_added__gte=days_ago_limit).order_by('date_added')[:1]
        profit = 0
        buy_price = 0
        for old_ticker in ticker_business_days_ago:
            if old_ticker.cb_buy_value_50:
                buy_price = old_ticker.cb_buy_value_50
                profit = sell_price - buy_price
        data = {
                'id': ticker.id,
                'date': ticker.date_added,
                'sell_price': sell_price,
                'buy_price': buy_price,
                'profit': profit
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
    #today_baseline = datetime(today.year, today.month, today.day)
    last_day_baseline = today - timedelta(days=1)
    daily_ticker_queryset = TickerHistory.objects.filter(id__gte=settings.CB_STARTING_ID,
                                                         date_added__gte=last_day_baseline).exclude(cb_buy_value=None)
    #: We go through results in reverse order so that the first record for each day is most recent data:
    daily_ticker_queryset = daily_ticker_queryset.order_by('date_added').reverse()
    
    daily_ticker_data = []
    cb_bs_ticker_data = []

    for ticker in daily_ticker_queryset:
        sell_price = Decimal(str(((ticker.sell_value * 50) - foreign_wire_fee - domestic_wire_fee)))
        sell_price *= fee_schedule_multiplier
        data = {
                'id': ticker.id,
                'date': ticker.date_added,
                'sell_price': sell_price,
                'buy_price': ticker.cb_buy_value_50,
                'profit': sell_price - ticker.cb_buy_value_50
                }
        daily_ticker_data.append(data)
        cb_bs_data = {
                      'date': ticker.date_added,
                      'cb_buy_price': ticker.cb_buy_value_50,
                      'bs_ask_price': ticker.bs_ask * 50,
                      'bs_bid_price': ticker.bs_bid * 50
                      }
        cb_bs_ticker_data.append(cb_bs_data)
        
    daily_ticker_data.reverse()
    daily_ticker_data = {
                         'total': len(daily_ticker_data),
                         'data': daily_ticker_data
                         }
    
    cb_bs_ticker_data.reverse()
    cb_bs_ticker_data = {
                         'total': len(cb_bs_ticker_data),
                         'data': cb_bs_ticker_data
                         }
    
    env = {
           'ticker_data': ticker_data,
           'daily_ticker_data': daily_ticker_data,
           'cb_bs_ticker_data': cb_bs_ticker_data,
           'form': form
           }
    return render_to_response('historical.html', RequestContext(request, env))

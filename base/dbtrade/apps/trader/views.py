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
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from dbtrade.apps.trader.models import TickerHistory, EmailNotice, IntervalHistory


def logout(request):
    return auth_logout(request, next_page="/")


fee_defaults = {
                'business_days_delay': 2,
                'foreign_wire_fee': Decimal('20.5'),
                'domestic_wire_fee': Decimal('45'),
                'fee_schedule': Decimal('0.6'),
                'increment': 50
                }



class FeeSelectorSimple(forms.Form):
    fee_schedule = forms.DecimalField(initial=fee_defaults['fee_schedule'])


class FeeSelector(forms.Form):
    business_days_delay = forms.IntegerField(initial=fee_defaults['business_days_delay'])
    foreign_wire_fee = forms.DecimalField(initial=fee_defaults['foreign_wire_fee'])
    domestic_wire_fee = forms.DecimalField(initial=fee_defaults['domestic_wire_fee'])
    fee_schedule = forms.DecimalField(initial=fee_defaults['fee_schedule'])
    increment = forms.IntegerField(initial=fee_defaults['increment'])
    

def _get_chart_data(business_days_delay, foreign_wire_fee, domestic_wire_fee, fee_schedule, increment):
    
    cache_key = '_get_chart_data-%s-%s-%s-%s-%s' % (str(business_days_delay), str(foreign_wire_fee),
                                                    str(domestic_wire_fee), str(fee_schedule), str(increment))
    cached_val = cache.get(cache_key)
    cache_len = 60 * 10
    
    if cached_val != None:
        return cached_val
    
    fee_schedule_multiplier = (Decimal('100') - Decimal(str(fee_schedule))) / Decimal('100')
    
    days_limit = 15
    date_limit = datetime.utcnow() - timedelta(days=days_limit)
    date_limit = str(date_limit).split(' ')[0]#dirty floor :p
    
    #===========================================================================
    # ticker_queryset = TickerHistory.objects.filter(id__gte=settings.CB_STARTING_ID).exclude(cb_buy_value=None)
    # ticker_queryset = ticker_queryset.order_by('date_added').reverse()
    #===========================================================================
    
    interval_queryset = IntervalHistory.objects.filter(date_added__gte=date_limit, interval='DAILY'
                                                       ).exclude(ticker=None
                                                       ).order_by('date_added').reverse()
    interval_queryset = interval_queryset.select_related()
    
    ticker_data = []
    last_date = None
    total_dates = 0
    for interval in interval_queryset:
        #: Deprecated:
        current_date = str(interval.date_added).split(' ')[0]
        if current_date == last_date:
            continue
        #: End deprecated
        total_dates += 1
        last_date = current_date
        try:
            sell_price = Decimal(str(((interval.ticker.sell_value * increment) - foreign_wire_fee - domestic_wire_fee)))
        except TypeError:
            sell_price = Decimal('0')
        sell_price *= fee_schedule_multiplier
        
        days_ago_limit = bus_days_ago(interval.date_added, business_days_delay)
        ticker_business_days_ago = IntervalHistory.objects.filter(
                                    date_added__gte=days_ago_limit).order_by('date_added')[:1]
        profit = 0
        buy_price = 0
        for interval in ticker_business_days_ago:
            old_ticker = interval.ticker
            #: Loops max of once
            if increment == 50 and old_ticker.cb_buy_value_50:
                buy_price = old_ticker.cb_buy_value_50
                profit = sell_price - buy_price
            elif old_ticker.cb_buy_value:
                buy_price = old_ticker.cb_buy_value * increment
                profit = sell_price - buy_price
            #: Don't set profit if there's no buy data available.  Historical from test site data.
        data = {
                'id': interval.ticker.id,
                'date': interval.date_added,
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
    #===========================================================================
    # daily_ticker_queryset = TickerHistory.objects.filter(id__gte=settings.CB_STARTING_ID,
    #                                                      date_added__gte=last_day_baseline).exclude(cb_buy_value=None)
    # #: We go through results in reverse order so that the first record for each day is most recent data:
    # daily_ticker_queryset = daily_ticker_queryset.order_by('date_added').reverse()
    #===========================================================================
    
    interval_queryset = IntervalHistory.objects.filter(date_added__gte=last_day_baseline, interval='HOURLY'
                                                       ).exclude(ticker=None
                                                       ).order_by('date_added').reverse()
                                                      
    interval_queryset = interval_queryset.select_related('ticker')
    
    daily_ticker_data = []
    cb_bs_ticker_data = []

    for interval in interval_queryset:
        try:
            sell_price = Decimal(str(((interval.ticker.sell_value * increment) - foreign_wire_fee - domestic_wire_fee)))
        except TypeError:#: NULL
            sell_price = Decimal('0')
        sell_price *= fee_schedule_multiplier
        if increment == 50:
            cb_buy_price = interval.ticker.cb_buy_value_50
            cb_sell_price = interval.ticker.cb_sell_value_50
        else:
            cb_buy_price = interval.ticker.cb_buy_value * increment
            cb_sell_price = interval.ticker.cb_sell_value * increment
        data = {
                'id': interval.ticker.id,
                'date': interval.date_added,
                'sell_price': sell_price,
                'buy_price': cb_buy_price,
                'profit': sell_price - cb_buy_price
                }
        daily_ticker_data.append(data)
        cb_bs_data = {
                      'date': interval.date_added,
                      'cb_buy_price': cb_buy_price,
                      'cb_sell_price': cb_sell_price,
                      'bs_ask_price': interval.ticker.bs_ask * increment,
                      'bs_bid_price': interval.ticker.bs_bid * increment
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
           'increment': increment,
           }
    cache.set(cache_key, env, cache_len)
    return env


def home(request):
    if request.user.is_authenticated():
        if not request.user.usersettings.coinbase_oauth_token:
            return HttpResponseRedirect('/historical/')
        else:
            return HttpResponseRedirect('/trade/')
    
    fields_set = False
    for field in fee_defaults:
        if field in request.GET:
            fields_set = True
    
    business_days_delay = 0
    foreign_wire_fee = 0
    domestic_wire_fee = 0
    fee_schedule = fee_defaults['fee_schedule']
    increment = 1
    
    if fields_set:
        form = FeeSelectorSimple(request.GET)
    else:
        form = FeeSelectorSimple()
    
    if form.is_valid():
        cleaned_data = form.clean()
        fee_schedule = cleaned_data['fee_schedule']
        
    most_recent_ticker_queryset = TickerHistory.objects.exclude(cb_buy_value=None).order_by('id').reverse()[:1]
    most_recent_ticker = most_recent_ticker_queryset[0]
    cost_1 = most_recent_ticker.cb_buy_value
    usd_50 = (float(1) / float(cost_1)) * 50
    
    env = _get_chart_data(business_days_delay, foreign_wire_fee, domestic_wire_fee, fee_schedule, increment)
    env['feeform'] = form
    env['profit_name'] = 'Difference'
    env['50_usd'] = '%.6f' % usd_50
    return auth_login(request, template_name='home.html', extra_context=env)


def about(request):
    env = {}
    return render_to_response('about.html', RequestContext(request, env))

    
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


@login_required(login_url='/#login-form')
def historical(request):
    
    fields_set = False
    for field in fee_defaults:
        if field in request.GET:
            fields_set = True
    
    business_days_delay = fee_defaults['business_days_delay']
    foreign_wire_fee = fee_defaults['foreign_wire_fee']
    domestic_wire_fee = fee_defaults['domestic_wire_fee']
    fee_schedule = fee_defaults['fee_schedule']
    increment = fee_defaults['increment']
            
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
        increment = cleaned_data['increment']
        
    env = _get_chart_data(business_days_delay, foreign_wire_fee, domestic_wire_fee, fee_schedule, increment)
    env['form'] = form
    env['profit_name'] = 'Potential Profit'
    return render_to_response('historical.html', RequestContext(request, env))


class EmailNoticeForm(forms.ModelForm):
    class Meta:
        model = EmailNotice
        fields = ['email', 'high_price_point', 'low_price_point', 'market', 'frequency', 'max_send']


def notification(request, uuid=None):
    if request.GET.get('email', None) != None and uuid == None:
        request.session['email'] = request.GET['email']
        return HttpResponseRedirect('/notification/')
    
    saved = 'saved' in request.GET and uuid != None
    
    if uuid:
        try:
            notification = EmailNotice.objects.get(uuid=uuid)
        except EmailNotice.DoesNotExist:
            raise Http404
        else:
            edit = True
            if request.method == 'POST':
                form = EmailNoticeForm(request.POST, instance=notification)
            else:
                form = EmailNoticeForm(instance=notification)
    else:
        notification = None
        edit = False
        if request.method == 'POST':
            form = EmailNoticeForm(request.POST)
        elif 'email' in request.session:
            form = EmailNoticeForm(initial={'email': request.session['email']})
        else:
            form = EmailNoticeForm()
    
    if edit:
        if 'cancel' in request.GET or 'activate' in request.GET:
            notification.active = 'activate' in request.GET
            notification.save()
            return HttpResponseRedirect('/notification/%s/?saved' % notification.uuid)
    
    if request.method == 'POST':
        if form.is_valid():
            notification = form.save()
            return HttpResponseRedirect('/notification/%s/?saved' % notification.uuid)
    
    env = {
           'form': form,
           'edit': edit,
           'saved': saved,
           'notification': notification,
           'uuid': uuid
           }
    return render_to_response('notification.html', RequestContext(request, env))


def login_coinbase(request):
    env = {'hide_top_login': True}
    return render_to_response('login_coinbase.html', RequestContext(request, env))

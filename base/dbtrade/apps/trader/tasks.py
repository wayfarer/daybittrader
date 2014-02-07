from datetime import timedelta, datetime
import time
from decimal import Decimal
from pprint import pprint

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.timezone import now

from celery.task import task
from celery.task import periodic_task
from celery.task.schedules import crontab

from dbtrade.apps.trader.models import TickerHistory, EmailNotice, EmailNoticeLog, TradeOrder, TradeOrderLog
from dbtrade.apps.trader.utils.my_api_client import API, CB_API
from dbtrade.apps.trader.utils.utils import auto_trade
from dbtrade.utils.utils import get_user_cb_api
from dbtrade.utils.apiclient import get_bitstamp_ticker
from dbtrade.utils.pusher import PusherClient


@task(queue='ticker', ignore_results=True, name='dbtrade.apps.trader.tasks.trader')
def trader(ticker_id):
    #: Deprecated
    current_ticker = TickerHistory.objects.get(id=ticker_id)
    auto_trade(current_ticker, buy_mode='hold', sell_mode='hold')


@periodic_task(queue='ticker', run_every=timedelta(seconds=600), ignore_result=True, name='dbtrade.apps.trader.tasks.ticker_save')
def ticker_save(*args, **kwargs):
    res = API.get_ticker()
    if res['result'] == 'success':
        ticker_data = res['data']
        cb_buy_value = CB_API.buy_price(1)
        cb_buy_value_50 = CB_API.buy_price(50)
        cb_sell_value = CB_API.sell_price(1)
        cb_sell_value_50 = CB_API.sell_price(50)
        bs_ticker = get_bitstamp_ticker()
        print 'bs_ticker= %s' % str(bs_ticker)
        print 'Saving ticker data!'
        #print ticker_data
        ticker_history = TickerHistory(volume=Decimal(ticker_data['vol']['value']),
                                       weighted_average_value=Decimal(ticker_data['vwap']['value']),
                                       weighted_average_value_int=int(ticker_data['vwap']['value_int']),
                                       average_value=Decimal(ticker_data['avg']['value']),
                                       average_value_int=int(ticker_data['avg']['value_int']),
                                       last_value=Decimal(ticker_data['last']['value']),
                                       last_value_int=int(ticker_data['last']['value_int']),
                                       high_value=Decimal(ticker_data['high']['value']),
                                       high_value_int=int(ticker_data['high']['value_int']),
                                       low_value=Decimal(ticker_data['low']['value']),
                                       low_value_int=int(ticker_data['low']['value_int']),
                                       sell_value=Decimal(ticker_data['sell']['value']),
                                       sell_value_int=int(ticker_data['sell']['value_int']),
                                       buy_value=Decimal(ticker_data['buy']['value']),
                                       buy_value_int=int(ticker_data['buy']['value_int']),
                                       cb_buy_value=cb_buy_value,
                                       cb_buy_value_50=cb_buy_value_50,
                                       cb_sell_value=cb_sell_value,
                                       cb_sell_value_50=cb_sell_value_50,
                                       bs_ask = bs_ticker['ask'],
                                       bs_bid = bs_ticker['bid'],
                                       bs_high = bs_ticker['high'],
                                       bs_last = bs_ticker['last'],
                                       bs_low = bs_ticker['low'],
                                       bs_volume = bs_ticker['volume'],
                                       mtgox_timestamp=ticker_data['now'],
                                       )
        ticker_history.save()
        trader.delay(ticker_history.id)
        do_trades.delay(str(ticker_history.cb_buy_value), str(ticker_history.cb_sell_value))
        email_notice.delay(str(ticker_history.buy_value), str(ticker_history.cb_buy_value), str(ticker_history.bs_ask))
    else:
        print 'Ticker data result other than success: "%s"' % res['result']
        
        
@task(queue='notices', ignore_results=True, name='dbtrade.apps.trader.tasks.email_notice')
def email_notice(mtgox_price, coinbase_price, bitstamp_price):
    print 'mtgox_price=%s' % mtgox_price
    print 'coinbase_price=%s' % coinbase_price
    print 'bitstamp_price=%s' % bitstamp_price
    
    mtgox_price = Decimal(mtgox_price)
    coinbase_price = Decimal(coinbase_price)
    bitstamp_price = Decimal(bitstamp_price)
    
    timedeltas = {
                  'HOURLY': timedelta(hours=1),
                  'DAILY': timedelta(days=1),
                  'WEEKLY': timedelta(days=7)
                  }
    for market in ['mtgox', 'coinbase', 'bitstamp']:
        print 'Market %s' % market
        for point in ['high', 'low']:
            now = datetime.now()
            price = locals()['%s_price' % market]
            if point == 'high':
                point_extra = 'lte'
            else:
                point_extra = 'gte'
            kwargs = {
                      'market': market.upper(),
                      '%s_price_point__%s' % (point, point_extra): price,
                      'active': True
                      }
            print 'Querying for %s' % str(kwargs)
            universal_time_exclusion = now - timedeltas['HOURLY']
            emails = EmailNotice.objects.filter(**kwargs).exclude(last_sent__gte=universal_time_exclusion)
            print 'Found %d matching notices...' % emails.count()
            for email in emails:
                max_date = now - timedeltas[email.frequency]
                recent_logs = EmailNoticeLog.objects.filter(email_notice=email,date_added__gte=max_date)
                recent_log = recent_logs.order_by('id').reverse()[:1]
                try:
                    recent_log[0]
                except IndexError:
                    print 'No outgoing emails logged for %s range for %s' % (email.frequency, email.email)
                else:
                    #: We have sent another email within the window, for DAILY and WEEKLY folks.
                    print 'Previous outgoing email was sent at %s for %s. Skipping...' % (str(recent_log[0].date_added),
                                                                                          email.email)
                    continue
                
                if email.max_send != None and recent_logs.count() + 1 >= email.max_send:
                    email.active = False
                    
                message = '%s\nYour price notification was activated due to price of $%s on %s.\n\n' % (str(now),
                                                                                                        str(price),
                                                                                                        market)
                message += 'See latest charts at https://daybittrader.com/\n'
                message += 'Edit or cancel this notification: https://daybittrader.com/notification/%s' % email.uuid
                
                print 'Sending...'
                send_mail(subject='Bitcoin price notification for %s ($%s)' % (str(now), str(price)),
                          message=message, from_email='Bitcoin Notifications <%s>' % settings.EMAIL_HOST_USER,
                          recipient_list=[email.email])
                
                email.last_sent = datetime.now()
                email.save()
                

@periodic_task(queue='live_connect', run_every=timedelta(seconds=600), ignore_results=True,
               name='dbtrade.apps.trader.tasks.live_bs_connect')
def live_bs_connect():
    #: get latest cb_buy_value, cb_sell_value, bs_last, calculate baselines
    ticker = TickerHistory.objects.all().order_by('id').reverse()[:1][0]
    buy_baseline = ticker.cb_buy_value / ticker.bs_last
    sell_baseline = ticker.cb_sell_value / ticker.bs_last
    print 'Starting live_bs_connect'
    print 'buy_baseline=%s' % str(buy_baseline)
    print 'sell_baseline=%s' % str(sell_baseline)
    
    c = PusherClient(settings.BS_PUSHER_APP_ID)
    event, data = c.get_data()
    print event
    print data
    
    c.subscribe('live_trades')
    event, data = c.get_data()
    print event
    print data
    
    start_time = time.time()
    timeout_length = 600#: 10 minutes
    while True:
        event, data = c.get_data()
        if event == 'trade':
            print data
            estimated_buy_price = Decimal(str(data['price'])) * buy_baseline
            estimated_sell_price = Decimal(str(data['price'])) * sell_baseline
            do_trades.delay(str(estimated_buy_price), str(estimated_sell_price))
        if time.time() - start_time >= timeout_length:
            #: Don't continue past timeout_length.  A new task with new price baselines will replace this one
            c.close()
            break
        
        
@task(queue='do_trades', ignore_results=True, name='dbtrade.apps.trader.tasks.do_trades')
def do_trades(estimated_buy_price, estimated_sell_price):
    print 'estimated_buy_price=%s' % estimated_buy_price
    print 'estimated_sell_price=%s' % estimated_sell_price
    estimated_buy_price = Decimal(estimated_buy_price)
    estimated_sell_price = Decimal(estimated_sell_price)
    
    def _queue_trades(*args):
        for trade_queryset in args:
            #: This makes it so the for loop doesn't work:
            #trade_orders = trade_queryset.select_for_update()
            #trade_queryset.update(locked=True)
            for trade_order in trade_queryset:
                print trade_order.id
                trade_order.locked = True
                trade_order.save()
                trade.delay(trade_order.id)
    
    _trade_queryset_shared = TradeOrder.objects.filter(locked=False, active=True, date_expire__gt=now())
    buy_trades = _trade_queryset_shared.filter(type='BUY', price_point__gte=estimated_buy_price)
    sell_trades = _trade_queryset_shared.filter(type='SELL', price_point__lte=estimated_sell_price)
    stoploss_trades = _trade_queryset_shared.filter(type='STOP_LOSS', price_point__gte=estimated_sell_price)
    _queue_trades(buy_trades, sell_trades, stoploss_trades)


@task(queue='trade', ignore_results=True, name='dbtrade.apps.trader.tasks.trade')
def trade(trade_id):
    try:
        trade_order = TradeOrder.objects.get(id=trade_id)
    except TradeOrder.DoesNotExist:
        print 'Trade id: %d does not exist!' % trade_id
        return
    if not trade_order.active:
        print 'Trade is not active, fails sanity check!'
        return
    
    print 'trade(%d)' % trade_id
    
    CB_API = get_user_cb_api(trade_order.user)
    if not CB_API:
        error_message = 'Oauth credentials not valid!'
        print error_message
        trade_order.active = False
        trade_order.locked = False
        trade_order.completion_status = 'FAIL'
        trade_order.save()
        TradeOrderLog(trade_order=trade_order, type=trade_order.type, btc_amount=trade_order.btc_amount,
                      status='FAIL', message=error_message).save()
        return
    
    if trade_order.type == 'SELL' or trade_order.type == 'STOP_LOSS':
        quote_price = CB_API.sell_price(float(trade_order.btc_amount))
    elif trade_order.type == 'BUY':
        quote_price = CB_API.buy_price(float(trade_order.btc_amount))
    
    requested_quote = trade_order.price_point * trade_order.btc_amount
    if trade_order.type == 'SELL':
        do_trade = quote_price >= requested_quote
    elif trade_order.type == 'BUY' or trade_order.type == 'STOP_LOSS':
        do_trade = quote_price <= requested_quote
        
    if do_trade:
        if trade_order.type == 'SELL' or trade_order.type == 'STOP_LOSS':
            result = CB_API.sell(float(trade_order.btc_amount))
        elif trade_order.type == 'BUY':
            result = CB_API.buy(float(trade_order.btc_amount))
        
        if result['success']:
            status='SUCCESS'
            message = None
            price_point = Decimal(result['transfer']['total']['amount']) / trade_order.btc_amount
        else:
            status = 'FAIL'
            message = result['errors'][0]
            price_point = None
        
        trade_order.active = False
        trade_order.locked = False
        trade_order.completion_status = status
        trade_order.save()
        TradeOrderLog(trade_order=trade_order, type=trade_order.type, btc_amount=trade_order.btc_amount,
                      price_point=price_point, status=status, message=message).save()
    else:
        error_message = 'Not performing trade due to quote of %f.' % quote_price
        print error_message
        trade_order.locked = False
        trade_order.save()
        TradeOrderLog(trade_order=trade_order, type=trade_order.type, btc_amount=trade_order.btc_amount,
                      status='FAIL', message=error_message).save()

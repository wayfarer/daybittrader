from datetime import timedelta, datetime
#from datetime import datetime
from decimal import Decimal
from pprint import pprint

from django.conf import settings
from django.core.mail import send_mail

from celery.task import task
from celery.task import periodic_task
from celery.task.schedules import crontab

from dbtrade.apps.trader.models import TickerHistory, EmailNotice, EmailNoticeLog
from dbtrade.apps.trader.utils.my_api_client import API, CB_API
from dbtrade.apps.trader.utils.utils import auto_trade
from dbtrade.utils.apiclient import get_bitstamp_ticker


@task(ignore_results=True, name='dbtrade.apps.trader.tasks.trader')
def trader(ticker_id):
    current_ticker = TickerHistory.objects.get(id=ticker_id)
    auto_trade(current_ticker, buy_mode='hold', sell_mode='hold')


@periodic_task(run_every=timedelta(seconds=600), ignore_result=True)
def ticker_save(*args, **kwargs):
    res = API.get_ticker()
    if res['result'] == 'success':
        ticker_data = res['data']
        cb_buy_value = CB_API.buy_price(1)
        cb_buy_value_50 = CB_API.buy_price(50)
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
        email_notice.delay(ticker_history.buy_value, ticker_history.cb_buy_value, ticker_history.bs_ask)
    else:
        print 'Ticker data result other than success: "%s"' % res['result']
        
        
@task(ignore_results=True, name='dbtrade.apps.trader.tasks.email_notice')
def email_notice(mtgox_price, coinbase_price, bitstamp_price):
    timedeltas = {
                  'HOURLY': timedelta(hours=1),
                  'DAILY': timedelta(days=1),
                  'WEEKLY': timedelta(days=7)
                  }
    for market in ['mtgox', 'coinbase', 'bitstamp']:
        for point in ['high', 'low']:
            now = datetime.now()
            price = locals()['%s_price' % market]
            kwargs = {
                      'market': market.upper(),
                      '%s_price_point' % point: price,
                      'active': True
                      }
            universal_time_exclusion = now - timedeltas['HOURLY']
            emails = EmailNotice.objects.filter(**kwargs).exclude(last_sent__gte=universal_time_exclusion)
            for email in emails:
                max_date = now - timedeltas[email]
                recent_logs = EmailNoticeLog.objects.filter(email_notice=email,date_added__gte=max_date)
                recent_log = recent_logs.order_by('id').reverse()[:1]
                try:
                    recent_log[0]
                except IndexError:
                    #: We have sent another email within the window, we exclude DAILY and WEEKLY folks here
                    continue
                if email.max_send != None and recent_logs.count() + 1 >= email.max_send:
                    email.active = False
                    email.save()
                message = 'Your price notification was activated due to price of $%s on %s\n' % (price, market)
                #: TODO: add deactivate/edit link
                send_mail(subject='Bitcoin price notification for %s' % str(now),
                          message=message, from_email='Bitcoin Notifications <%s>' % settings.EMAIL_HOST_USER,
                          recipient_list=[email.email])
        

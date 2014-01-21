import os, sys
import time
import random
from datetime import datetime, timedelta

#from django.utils.thread_support import currentThread
from oauth2client.client import AccessTokenRefreshError

from dbtrade.apps.trader.utils.my_api_client import API, CoinBaseAPI
from dbtrade.apps.trader.models import UserSettings


BTC_INT_FACTOR = 100000000
USD_INT_FACTOR = 100000


#: The following causes and error in this version of Django because django.utils.thread_support is gone:
#===============================================================================
# _requests = {}
# 
# def get_request():
#     return _requests[currentThread()]
#===============================================================================


class GlobalRequestMiddleware(object):
    def process_request(self, request):
        #_requests[currentThread()] = request
        if request.user.is_authenticated():
            try:
                user_settings = UserSettings.objects.get(user=request.user)
            except UserSettings.DoesNotExist:
                user_settings = UserSettings(user=request.user)
                user_settings.save()
            if 'current_cb_balance' not in request.session or \
            request.session['current_cb_balance']['expires'] < datetime.utcnow():
                CB_API = get_user_cb_api(request.user)
                if CB_API != None:
                    request.session['current_cb_balance'] = {
                                                             'amount': CB_API.balance,
                                                             'expires': datetime.utcnow() + timedelta(hours=4)
                                                             }


def clear_all_bids():
    orders = API.get_orders()
    #print orders
    for order in orders['data']:
        if order['type'] == 'bid':
            print 'Canceling %s' % order['oid']
            API.cancel_order(order['oid'])


def tickle_bids(low, high, amountlow=.02, amounthigh=.09, concurrent=4, pause=33.5):
    try:
        while True:
            time.sleep(pause)
            clear_all_bids()
            amount_midpoint = amounthigh - ((amounthigh - amountlow) / 2)
            bid_amounts = []
            for i in range(concurrent):
                bid_btc_amount = float("{0:.4f}".format(random.triangular(amountlow,
                                                                      amounthigh,
                                                                      amount_midpoint)))
                bid_amounts.append(bid_btc_amount)
            
            bid_price_midpoint = float(high) - ((float(high) - float(low)) / 2)
            print 'Bid price midpoint: %f' % bid_price_midpoint
            for bid_btc_amount in bid_amounts:
                bid = float("{0:.2f}".format(random.triangular(low, high, bid_price_midpoint)))
                print 'Bid: %f [%f]' % (bid, bid_btc_amount)
                total_btc_int = int(bid_btc_amount * BTC_INT_FACTOR)
                buy_price_int = int(bid * USD_INT_FACTOR)
                res = API.add_order('bid', total_btc_int, buy_price_int)
                print res
            
    except KeyboardInterrupt:
        print '\nStopping...'
        clear_all_bids()
        
        
def get_user_cb_api(user):
    token_json = user.usersettings.coinbase_oauth_token
    if not token_json:
        return None
    #: TODO, check if result is JSON serializable, then migrate to encrypted form for future security
    CB_API = CoinBaseAPI(oauth2_credentials=token_json)
    if CB_API.token_expired:
        print 'Token expired, attempting refresh...'
        try:
            token = CB_API.refresh_oauth()
            user.usersettings.coinbase_oauth_token = token.to_json()
            user.usersettings.save()
        except AccessTokenRefreshError:
            print 'AccessTokenRefreshError'
            return None
    return CB_API

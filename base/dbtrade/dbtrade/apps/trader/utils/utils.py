from decimal import Decimal
from pprint import pprint

from dbtrade.apps.trader.models import TickerHistory, OrderRecord
from dbtrade.apps.trader.utils.my_api_client import API

BTC_INT_FACTOR = 100000000
USD_INT_FACTOR = 100000


def auto_trade(current_ticker=None, buy_mode='moderate', sell_mode='moderate'):
    allowed_modes = ['moderate', 'aggressive', 'bull', 'cautious', 'bear', 'hold']
    if buy_mode not in allowed_modes:
        print 'Disallowed buy mode! (%s)' % buy_mode
        return False
    if sell_mode not in allowed_modes:
        print 'Disallowed sell mode! (%s)' % sell_mode
        return False
    
    print 'Sell mode: %s' % sell_mode
    print 'Buy mode: %s' % buy_mode
    
    if current_ticker == None:
        current_ticker = TickerHistory.objects.all().order_by('id').reverse()[:1][0]
    
    last_price = current_ticker.last_value
    high_price = current_ticker.high_value
    low_price = current_ticker.low_value
    medium_price = current_ticker.weighted_average_value
    
    high_med_diff = high_price - medium_price
    med_low_diff = medium_price - low_price
    
    #: TODO: update as weighted percentage, instead of 1/2 (?)
    high_medium = medium_price + (high_med_diff / 2)
    low_medium = low_price + (med_low_diff / 2)
    print """
    Last:  %f
    High:  %f
    Low:   %f
    Med:   %f
    Hdiff: %f
    Ldiff: %f
    Hmid:  %f
    Lmid:  %f
    """ % (last_price, high_price, low_price, medium_price, high_med_diff, med_low_diff,
           high_medium, low_medium)
    
    #: HOW THIS WORKS
    #: If we're in a buy state (need to buy), we place a buy order at the Lmid (low_medium) price
    #: Once there has been buy order, we're in a sell state until we let go of our coins
    #: IF WE'RE IN A SELL STATE:
    #: We place a sell order at the Hmid price (high_medium), until it sells.
    #: BOTH:
    #: We don't just wait around for it to buy/sell, we constantly cancel the last buy/sell order
    #: and place a new order until we get there.  This keeps the orders up to date with current
    #: market conditions.
    
    
    account_info_result = API.get_account_info()
    if account_info_result['result'] == 'success':
        account_info = account_info_result['data']
    else:
        print 'Error retrieving account info!'
        return False
    #pprint(account_info)
    wallet = {
              'btc': {
                      'value': Decimal(account_info['Wallets']['BTC']['Balance']['value']),
                      'value_int': int(account_info['Wallets']['BTC']['Balance']['value_int'])
                      },
              'usd': {
                      'value': Decimal(account_info['Wallets']['USD']['Balance']['value']),
                      'value_int': int(account_info['Wallets']['USD']['Balance']['value_int'])
                      }
              }
    #pprint(wallet)
    
    if buy_mode == 'moderate':
        buy_price = low_medium
    elif buy_mode == 'aggressive':
        buy_price = medium_price
    elif buy_mode == 'cautious':
        buy_price = low_price
    elif buy_mode == 'bear':
        pass#:TODO: need ability to bet below low_price first
    elif buy_mode == 'bull':
        pass#:TODO: need ability to bet above high_price first
    elif buy_mode == 'hold':
        buy_price = 0
    
    if sell_mode == 'moderate':
        sell_price = high_medium
    elif sell_mode == 'aggressive':
        sell_price = high_price
    elif sell_mode == 'cautious':
        sell_price = medium_price
    elif sell_mode == 'bear':
        pass#:TODO: need ability to bet below low_price first
    elif sell_mode == 'bull':
        pass#:TODO: need ability to bet above high_price first
    elif sell_mode == 'hold':
        sell_price = 1000000
        
    print 'Sell price is: %f' % sell_price
    print 'Buy price is: %f' % buy_price
    print '----'
    
    def _update_buy_orders(cancel=True):
        buy_orders = OrderRecord.objects.filter(type='BUY', status='OPEN')
        for buy_order in buy_orders:
            #res = API.get_order_result(buy_order.oid)
            #print 'Previous Buy Order Result:'
            #pprint(res)
            #: TODO: improve logic?
            try:
                API.cancel_order(buy_order.oid)
            except:
                print 'Buy order cannot be canceled, probably because it was completed.'
                
            if wallet['btc']['value'] >= buy_order.btc_value * Decimal('.994'):
                print 'Previous buy order is marked as COMPLETE'
                buy_order.status = 'COMPLETED'
            elif cancel:
                print 'Previous buy order is marked as CANCELED'
                buy_order.status = 'CANCELED'
            buy_order.save()
            
    def _update_sell_orders(cancel=True):
        sell_orders = OrderRecord.objects.filter(type='SELL', status='OPEN')
        for sell_order in sell_orders:
            #res = API.get_order_result(sell_order.oid)
            #print 'Previous Sell Order Result:'
            #pprint(res)
            #: TODO: improve logic?
            try:
                API.cancel_order(sell_order.oid)
            except:
                print 'Buy order cannot be canceled, probably because it was completed.'
            if wallet['usd']['value'] >= sell_order.usd_value * Decimal('.994'):
                print 'Previous sell order is marked as COMPLETE'
                sell_order.status = 'COMPLETED'
            elif cancel:
                print 'Previous sell order is marked as CANCELED'
                sell_order.status = 'CANCELED'
            sell_order.save()
            
    #: If there are any prior Buy orders, cancel them.  If there is any money in the account,
    #: create calculated Buy order.
    
    #: must have at least $20 in account or it won't buy
    
    if wallet['usd']['value'] > 20 and buy_mode != 'hold':
        print 'Buying...'
        print 'Wallet: %d' % wallet['usd']['value_int']
        total_btc = wallet['usd']['value_int'] / (buy_price * USD_INT_FACTOR)
        total_btc_int = int(total_btc * BTC_INT_FACTOR)
        print 'Buy Price: %f' % buy_price
        print 'Total BTC: %f' % total_btc
        print 'Total BTC (int) %d' % total_btc_int
        
        _update_buy_orders()
        _update_sell_orders(False)
            
        buy_price_int = int(buy_price * USD_INT_FACTOR)
        
        res = API.add_order('bid', total_btc_int, buy_price_int)
        print 'Buy result:'
        #pprint(res)
        print res
        if res['result'] == 'success':
            buy_order = OrderRecord(oid=res['data'], type='BUY', btc_value=total_btc,
                                    btc_value_int=total_btc_int, usd_value=wallet['usd']['value'],
                                    usd_value_int=wallet['usd']['value_int'])
            buy_order.save()
    
    #: If there are any prior Sell orders, cancel them.  If there is any bitcoins in the account,
    #: create calculated Sell order.
    
    #: Must have at least .1 BTC in wallet, or it won't sell
    
    if wallet['btc']['value'] > .1 and sell_mode != 'hold':
        print 'Selling...'
        print 'Wallet: %d' % wallet['btc']['value_int']
        total_btc = wallet['btc']['value']
        total_btc_int = wallet['btc']['value_int']
        print 'Sell Price: %f' % sell_price
        print 'Total BTC: %f' % total_btc
        print 'Total BTC (int) %d' % total_btc_int
        
        _update_buy_orders(False)
        _update_sell_orders()
        
        sell_price_int = int(sell_price * USD_INT_FACTOR)
        sell_usd_value = sell_price * total_btc
        sell_usd_value_int = int(sell_usd_value * USD_INT_FACTOR)
        
        res = API.add_order('ask', total_btc_int, sell_price_int)
        print 'Sell result:'
        #pprint(res)
        print res
        if res['result'] == 'success':
            buy_order = OrderRecord(oid=res['data'], type='SELL', btc_value=total_btc,
                                    btc_value_int=total_btc_int, usd_value=sell_usd_value,
                                    usd_value_int=sell_usd_value_int)
            buy_order.save()
    
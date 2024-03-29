import os, sys
import time
import random

from dbtrade.apps.trader.utils.my_api_client import API


BTC_INT_FACTOR = 100000000
USD_INT_FACTOR = 100000

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

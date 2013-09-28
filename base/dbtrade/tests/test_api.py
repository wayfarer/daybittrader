#!/usr/bin/env python

import sys, os
import json
from pprint import pprint

sys.path.append('../..')

from dbtrade.apps.trader.utils.my_api_client import API

def main():
    #res = API.get_ticker()
    #res = API.get_order_lag()
    #res = API.add_order(type='bid', amount=10000, price_int=10)
    res = API.get_order_quote(type='bid', amount=100000000)
    if res['result'] == 'success':
        ticker_data = res['data']
        pprint(ticker_data)
    else:
        print res['result']

if __name__ == '__main__':
    main()
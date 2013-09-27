#!/usr/bin/env python

import sys, os
#import json
#from pprint import pprint

sys.path.append('../..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dbtrade.settings")

from dbtrade.apps.trader.utils.utils import auto_trade
    
if __name__ == '__main__':
    auto_trade(buy_mode='cautious', sell_mode='aggressive')

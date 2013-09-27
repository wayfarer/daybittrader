#!/usr/bin/env python

import sys, os
import json
from pprint import pprint

sys.path.append('../..')

from dbtrade.apps.trader.utils.my_api_client import CB_API

def main():
    print CB_API.buy_price(50)

if __name__ == '__main__':
    main()
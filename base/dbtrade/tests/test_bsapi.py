#!/usr/bin/env python

import sys, os
from pprint import pprint

sys.path.append('../..')

from dbtrade.utils.apiclient import get_bitstamp_ticker

def main():
    pprint(get_bitstamp_ticker())

if __name__ == '__main__':
    main()
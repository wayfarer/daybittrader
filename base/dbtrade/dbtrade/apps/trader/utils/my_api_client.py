import sys, os
import json

from dbtrade.utils.apiclient import MtGoxAPI, CoinBaseAPI

fpath = os.path.realpath(os.path.join(os.path.realpath(__file__), '../../../../../../../auth.json'))
with open(fpath, 'r') as f:
    api_keys = json.loads(f.read())
    
#print type(api_keys['cb_key'])
    
API = MtGoxAPI(api_keys['key'], api_keys['secret'])
CB_API = CoinBaseAPI(api_key=str(api_keys['cb_key']))
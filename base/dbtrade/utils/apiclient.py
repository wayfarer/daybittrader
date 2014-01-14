import hmac, base64, hashlib, urllib, urllib2, time, json, time

from coinbase import CoinbaseAccount
from django.conf import settings
from oauth2client.client import OAuth2WebServerFlow

class MtGoxAPI(object):
    
    def __init__(self, key, secret, currency='USD', api_version=2, retry_level=3):
        self.key = key
        self.secret = base64.b64decode(secret)
        self.api_version = api_version
        self.currency = currency
        self.retry_level = retry_level
        self.BASE_PATH = 'BTC%s/' % currency
        self.BASE_URL = 'https://data.mtgox.com/api/%d/%s' % (api_version, self.BASE_PATH)

    def do_request(self, path, data={}):
        post_data = urllib.urlencode(data)
        
        print 'Calling path "%s" with data: "%s"' % (path, post_data)
        
        nonce_amp = post_data and '&' or ''
        nonce_str = '%snonce=%s' % (nonce_amp, self._nonce())
        #: Make sure nonce argument is at end, which supposedly can matter
        post_data += nonce_str
        
        hash_data = self.BASE_PATH + path + chr(0) + post_data
        hmac_str = str(hmac.new(self.secret, hash_data, hashlib.sha512).digest())
        rest_sign = base64.b64encode(hmac_str)
    
        header = {
            'User-Agent': 'Day-BitTrader',
            'Rest-Key': self.key,
            'Rest-Sign': rest_sign,
            #'Accept-encoding': 'GZIP',
        }
        for i in range(self.retry_level + 1):
            try:
                json_resp = urllib2.urlopen(urllib2.Request(self.BASE_URL + path, post_data, header), post_data).read()
            except urllib2.HTTPError, e:
                if i == self.retry_level:
                    raise e
                else:
                    print 'Error: %s, retrying...' % str(e)
                    time.sleep(1)
                    continue
            else:
                break
        try:
            resp = json.loads(json_resp)
        except ValueError:
            return json_resp
        else:
            return resp
    
    def _nonce(self):
        return str(int(time.time() * 1e6))
    
    def get_ticker(self):
        return self.do_request('money/ticker')
    
    def get_fast_ticker(self):
        return self.do_request('money/ticker_fast')
    
    def get_account_info(self):
        return self.do_request('money/info')
    
    def get_idkey(self):
        return self.do_request('money/idkey')
    
    def get_orders(self):
        return self.do_request('money/orders')
    
    def get_currency_info(self):
        return self.do_request('money/currency')
    
    def get_order_quote(self, type, amount):
        """
        type: bid or ask
        amount: amount of BTC needed quote for
        """
        data = {'type': type, 'amount': amount}
        return self.do_request('money/order/quote', data)
    
    def add_order(self, type, amount_int, price_int=None):
        """
        type: bid or ask
        amount_int: amount of BTC needed quote for, as an integer
        price_int: optional, the price of the of the currency you wish to trade in
        """
        data = {'type': type, 'amount_int': amount_int}
        if price_int:
            data['price_int'] = price_int
            
        return self.do_request('money/order/add', data)
    
    def cancel_order(self, oid):
        """
        oid: the oid of the order to cancel
        """
        data = {'oid': oid}
        return self.do_request('money/order/cancel', data)
    
    def get_order_result(self, oid):
        data = {'oid': oid}
        return self.do_request('money/order/result', data)
    
    def get_order_lag(self):
        return self.do_request('money/order/lag')
    
    def get_trades(self, since=None):
        """
        All trades performed, not just YOUR trades!
        since: optional, UNIX microstamp from which to return trade data.
        If omitted, last 1000 trades are returned.
        """
        data = {}
        if since:
            data['since'] = since
        
        return self.do_request('money/trades/fetch', data)
    
    def get_depth_info(self):
        return self.do_request('money/depth/fetch')
    
    def get_depth_full(self):
        return self.do_request('money/depth/full')
    
    def get_wallet_history(self, currency='BTC', page=None):
        data = {'currency': currency}
        if page:
            data['page'] = page
        return self.do_request('money/wallet/history', data)
    
    def generate_hotp_key(self):
        return self.do_request('security/hotp/gen')
    
    def get_public_stream(self):
        return self.do_request('stream/list_public')
    
    #: TODO: implement undocumented methods:
    #: https://bitbucket.org/nitrous/mtgox-api/overview#markdown-header-other-methods
    
class CoinBaseAPI(CoinbaseAccount):
    pass


coinbase_client = OAuth2WebServerFlow(settings.COINBASE_ID, settings.COINBASE_SECRET, 'all',
                                      redirect_uri=settings.COINBASE_CALLBACK_URL,
                                      auth_uri='https://www.coinbase.com/oauth/authorize',
                                      token_uri='https://www.coinbase.com/oauth/token')


def get_bitstamp_ticker():
    """Super simple function that returns Bitstamp ticker info from public API"""
    request_uri = 'https://www.bitstamp.net/api/ticker/'
    #post_data = ''
    header = {
              'User-Agent': 'Day-BitTrader',
              }
    request = urllib2.Request(request_uri, headers=header)
    json_data = urllib2.urlopen(request).read()
    #json_data = urllib2.urlopen(urllib2.Request(request_uri, post_data, header), post_data).read()
    return json.loads(json_data)


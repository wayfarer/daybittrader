import uuid
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


class TimeStampModel(models.Model):
    #: Date added
    date_added = models.DateTimeField(auto_now_add=True)
    
    #: Date updated
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
class LogModel(models.Model):
    #: Date added
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True


class TickerHistory(LogModel):
    volume = models.DecimalField(max_digits=18, decimal_places=8, null=True)
    
    weighted_average_value  = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    weighted_average_value_int = models.IntegerField(null=True)
    
    average_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    average_value_int = models.IntegerField(null=True)
    
    last_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    last_value_int = models.IntegerField(null=True)
    
    high_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    high_value_int = models.IntegerField(null=True)
    
    low_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    low_value_int = models.IntegerField(null=True)
    
    sell_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    sell_value_int = models.IntegerField(null=True)
    
    buy_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    buy_value_int = models.IntegerField(null=True)
    
    cb_buy_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    cb_buy_value_50 = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    cb_sell_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    cb_sell_value_50 = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    
    bs_ask = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_bid = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_high = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_last = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_low = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_volume = models.DecimalField(max_digits=18, decimal_places=8, null=True)
    
    mtgox_timestamp = models.CharField(max_length=100, null=True)
    
    
class IntervalHistory(models.Model):
    #: Which ticker history.  Can be NULL, due to fact most recent ticker may not be recent enough, due to stuck worker
    ticker = models.OneToOneField(TickerHistory, null=True)
    
    #: HOURLY, DAILY, or WEEKLY
    interval = models.CharField(max_length=32, db_index=True)
    
    #: Date added is indexed for quick lookups
    date_added = models.DateTimeField(auto_now_add=True, db_index=True)
    


class OrderRecord(TimeStampModel):
    
    #: Order OID, according to MtGox
    oid = models.CharField(max_length=100, db_index=True)
    
    #: BUY, SELL
    type = models.CharField(max_length=32)
    
    #: OPEN, CANCELED, COMPLETED
    status = models.CharField(max_length=32, default='OPEN')
    
    #: Value, in BTC
    btc_value = models.DecimalField(max_digits=18, decimal_places=8)
    btc_value_int = models.IntegerField()
    
    #: Value, in USD
    usd_value = models.DecimalField(max_digits=12, decimal_places=5)
    usd_value_int = models.IntegerField()
    
    #: If True, when this bid is made, it does not get replaced every 5 minutes.
    hold = models.BooleanField(default=False)
    
    
MARKET_CHOICES = (('COINBASE', 'Coinbase'), ('MTGOX', 'MtGox'), ('BITSTAMP', 'Bitstamp'))
FREQUENCY_CHOICES = (('HOURLY', 'Hourly'), ('DAILY', 'Daily'), ('WEEKLY', 'Weekly'))


class EmailNotice(TimeStampModel):
    
    #: Unique identifier to allow administration of notification if you have the link
    uuid = models.CharField(max_length=36, db_index=True, null=True)
    
    #: Email address to send notifications to
    email = models.EmailField(max_length=254, help_text='Your email address')
    
    #: If price rises above this point, send notification
    high_price_point = models.DecimalField(max_digits=12, decimal_places=5, db_index=True,
                                           help_text='If price rises above this point, send notification ($USD)')
    
    #: If price falls below this point, send notification
    low_price_point = models.DecimalField(max_digits=12, decimal_places=5, db_index=True,
                                          help_text='If price falls below this point, send notification ($USD)')
    
    #: Market to use as price indicator. COINBASE, MTGOX, or BITSTAMP
    market = models.CharField(max_length=32, db_index=True, choices=MARKET_CHOICES,
                              help_text='Which market should be the key to notifications')
    
    #: How often to send notification: HOURLY, DAILY or WEEKLY
    frequency = models.CharField(max_length=32, choices=FREQUENCY_CHOICES,
                                 help_text='Maximum frequency to send notifications if price is in high or low range')
    
    #: Maximum amount of times to send notifications
    max_send = models.IntegerField(null=True, blank=True,
                                   help_text='Maximum number of notifications to send (leave blank for unlimited)')
    
    #: Whether to send notifications at all
    active = models.BooleanField(default=True)
    
    #: Last time email was sent.  For easy frequency selection
    last_sent = models.DateTimeField(default=datetime(1970, 1, 1, 0, 0, 0, 0), db_index=True)
    
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        
        super(EmailNotice, self).save(*args, **kwargs)


class EmailNoticeLog(models.Model):
    
    #: Which notification email and settings
    email_notice = models.ForeignKey(EmailNotice, null=True)
    
    #: HIGH or LOW
    notice_type = models.CharField(max_length=32)
    
    #: Recorded price
    price = models.DecimalField(max_digits=12, decimal_places=5)
    
    #: Market recorded price is from. COINBASE, MTGOX, or BITSTAMP.  Repeated here in case EmailNotice updated
    market = models.CharField(max_length=32)
    
    #: We don't use LogModel, because we need to index this field for timedelta searches for frequency calculation
    date_added = models.DateTimeField(auto_now_add=True, db_index=True)
    

TRADE_TYPE_CHOICES = (('BUY', 'Buy'), ('SELL', 'Sell'), ('STOP_LOSS', 'Stop Loss'))


class TradeOrder(TimeStampModel):
    
    #: Which user this trade belongs to
    user = models.ForeignKey(User, null=True)
    
    #: Don't execute trade until the parent trade has first been executed.  Can be used for buy/sell plans, etc
    parent_trade = models.ForeignKey('TradeOrder', null=True)
    
    #: Unique identifier for convenience of user
    uuid = models.CharField(max_length=36, db_index=True, null=True)
    
    #: Type of trade, BUY, SELL or STOP_LOSS
    type = models.CharField(max_length=32, choices=TRADE_TYPE_CHOICES, db_index=True)
    
    #: When to trade.  Low for BUY or STOP_LOSS, high for SELL
    price_point = models.DecimalField(max_digits=12, decimal_places=5, db_index=True,
                                      verbose_name='Trading Price',
                                      help_text='Your trade will be executed at this price point.')
    
    #: Amount to trade, in BTC.  In the future, we may allow purchasing in fiat amounts.
    btc_amount = models.DecimalField(max_digits=18, decimal_places=8, verbose_name='BTC Amount')
    
    #: Whether order is still active, or has been canceled.
    active = models.BooleanField(default=True, db_index=True)
    
    #: Used as a filter in special cases.  Sometimes we need to lock a job to make sure only one worker operates on
    #: it at a time in a distributed queue environment.  Worker that sends trade request needs to know not to resend,
    #: if that trade hasn't been completed yet.
    locked = models.BooleanField(default=False, db_index=False)
    
    #: SUCCESS or FAIL
    completion_status = models.CharField(max_length=32, null=True, db_index=True)
    
    #: When trade order expires.  We require this to be set, for now.
    date_expire = models.DateTimeField(db_index=True)
    
    @property
    def most_recent_log(self):
        log_queryset = TradeOrderLog.objects.filter(trade_order=self).order_by('id').reverse()[:1]
        try:
            log = log_queryset[0]
        except IndexError:
            return None
        else:
            return log
    
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        
        super(TradeOrder, self).save(*args, **kwargs)


class TradeOrderLog(LogModel):
    
    #: Which trade order
    trade_order = models.ForeignKey(TradeOrder)
    
    #: Type of trade, BUY or SELL.  Redundant
    type = models.CharField(max_length=32)
    
    #: Amount of BTC purchased.  Redundant.
    btc_amount = models.DecimalField(max_digits=18, decimal_places=8)
    
    #: The actual price traded at.  Could be lower or higher than original price point
    price_point = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    
    #: SUCCESS or FAIL
    status = models.CharField(max_length=32)
    
    #: Optional message desribing anything of interest to do with this trade.  Probably failure reason.
    message = models.TextField(null=True)


class UserSettings(models.Model):
    user = models.OneToOneField(User)
    coinbase_oauth_token = models.TextField(null=True)
    coinbase_user_id = models.CharField(max_length=64, null=True, db_index=True, unique=True)

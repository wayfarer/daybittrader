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
    weighted_average_value_int = models.IntegerField()
    
    average_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    average_value_int = models.IntegerField()
    
    last_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    last_value_int = models.IntegerField()
    
    high_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    high_value_int = models.IntegerField()
    
    low_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    low_value_int = models.IntegerField()
    
    sell_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    sell_value_int = models.IntegerField()
    
    buy_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    buy_value_int = models.IntegerField()
    
    cb_buy_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    cb_buy_value_50 = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    
    bs_ask = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_bid = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_high = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_last = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_low = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bs_volume = models.DecimalField(max_digits=18, decimal_places=8, null=True)
    
    mtgox_timestamp = models.CharField(max_length=100)


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


class UserSettings(models.Model):
    user = models.OneToOneField(User)
    coinbase_oauth_token = models.TextField(null=True)
